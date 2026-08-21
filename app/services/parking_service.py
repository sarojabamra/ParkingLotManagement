from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.constants import (
    IST,
    ParkingHistoryStatus,
    UserRole,
)
from app.models.parking_history import ParkingHistory
from app.models.parking_space import ParkingSpace
from app.models.user import User
from app.schemas.parking_history import (
    ParkingLockRequest,
    ParkingLockResponse,
    ParkingUnlockRequest,
    ParkingUnlockResponse,
)
from app.schemas.parking_space import (
    AdminAvailabilityResponse,
    PublicAvailabilityResponse,
)
from app.utils.fee import calculate_parking_fee
from app.utils.parking import (
    activate_booking,
    check_vehicle_active_parking_session,
    create_immediate_parking,
    decrease_parking_availability,
    find_parking_space,
    increase_parking_availability,
)


def get_availability(
    db: Session,
    current_user: User,
):
    parking_spaces = db.query(ParkingSpace).order_by(ParkingSpace.level).all()

    if current_user.role == UserRole.ADMIN:
        return [
            AdminAvailabilityResponse(
                level=space.level,
                two_wheeler_available=space.twa,
                four_wheeler_available=space.fwa,
            )
            for space in parking_spaces
        ]

    return [
        PublicAvailabilityResponse(
            level=space.level,
            two_wheeler_available=space.twa > 0,
            four_wheeler_available=space.fwa > 0,
        )
        for space in parking_spaces
    ]


def get_my_parking_history(db: Session, current_user: User):
    return (
        db.query(ParkingHistory)
        .filter(ParkingHistory.user_id == current_user.id)
        .order_by(ParkingHistory.in_time.desc())
        .all()
    )


def lock_parking(
    request: ParkingLockRequest,
    db: Session,
    current_user: User,
):
    parking_space = find_parking_space(db, request.level)
    current_time = datetime.now(IST)

    if check_vehicle_active_parking_session(db, request.vehicle_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle already has an active parking session.",
        )

    booking = (
        db.query(ParkingHistory)
        .filter(
            ParkingHistory.vehicle_number == request.vehicle_number,
            ParkingHistory.user_id == current_user.id,
            ParkingHistory.level == request.level,
            ParkingHistory.type == request.type,
            ParkingHistory.status == ParkingHistoryStatus.BOOKED,
        )
        .first()
    )

    if booking:
        parking_record = activate_booking(db, booking, request, current_time)

    else:
        parking_record = create_immediate_parking(
            db, request, current_user, current_time
        )

    decrease_parking_availability(parking_space, request.type)
    db.add(parking_record)
    db.commit()
    db.refresh(parking_record)

    return ParkingLockResponse(
        vehicle_number=parking_record.vehicle_number,
        type=parking_record.type,
        level=parking_record.level,
        lot=parking_record.lot,
        locking_time=parking_record.in_time,
        user_id=parking_record.user_id,
    )


def unlock_parking(
    db: Session,
    request: ParkingUnlockRequest,
    current_user: User,
):
    history = (
        db.query(ParkingHistory)
        .filter(
            ParkingHistory.vehicle_number == request.vehicle_number,
            ParkingHistory.level == request.level,
            ParkingHistory.lot == request.lot,
            ParkingHistory.user_id == current_user.id,
            ParkingHistory.status == ParkingHistoryStatus.ACTIVE,
        )
        .first()
    )

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active parking record not found for this vehicle and lot",
        )

    parking_space = find_parking_space(db, history.level)

    unlocking_time = datetime.now(IST)

    history.out_time = unlocking_time

    history.fee = calculate_parking_fee(
        history.type,
        history.in_time,
        unlocking_time,
        history.scheduled_out_time,
    )
    history.status = ParkingHistoryStatus.COMPLETED

    increase_parking_availability(parking_space, history.type)

    db.commit()
    db.refresh(history)

    return ParkingUnlockResponse(
        vehicle_number=history.vehicle_number,
        lot=history.lot,
        locking_time=history.in_time,
        unlocking_time=history.out_time,
        parking_fee=history.fee,
        user_id=history.user_id,
    )
