from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.constants import ParkingHistoryStatus, IST
from app.models.parking_history import ParkingHistory
from app.models.user import User
from app.schemas.parking_history import BookingCreate, BookingResponse
from app.utils.parking import (
    find_parking_space,
    get_available_lots,
    select_random_lot,
    auto_cancel_expired_bookings,
)


def get_my_bookings(db: Session, current_user: User):

    auto_cancel_expired_bookings(db, current_user.id)

    return (
        db.query(ParkingHistory)
        .filter(
            ParkingHistory.user_id == current_user.id,
            ParkingHistory.status == ParkingHistoryStatus.BOOKED,
        )
        .order_by(ParkingHistory.in_time.desc())
        .all()
    )


def create_booking(
    db: Session,
    request: BookingCreate,
    current_user: User,
):
    start_time = request.start_time.astimezone(IST)
    end_time = request.end_time.astimezone(IST)
    current_time = datetime.now(IST)

    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    if start_time <= current_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking must be for a future time",
        )

    find_parking_space(db, request.level)

    available_lots = get_available_lots(
        db,
        request.level,
        request.type,
        start_time,
        end_time,
        error_detail="No parking lots available for the requested booking time.",
    )

    selected_lot_number = select_random_lot(available_lots)

    booking = ParkingHistory(
        user_id=current_user.id,
        level=request.level,
        type=request.type,
        vehicle_number=request.vehicle_number,
        lot=selected_lot_number,
        in_time=start_time,
        scheduled_out_time=end_time,
        out_time=None,
        fee=None,
        status=ParkingHistoryStatus.BOOKED,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return BookingResponse(
        id=booking.id,
        vehicle_number=booking.vehicle_number,
        type=booking.type,
        level=booking.level,
        lot=booking.lot,
        start_time=booking.in_time,
        end_time=booking.scheduled_out_time,
        status=booking.status,
        user_id=booking.user_id,
    )


def cancel_booking(
    db: Session,
    booking_id: int,
    current_user: User,
):
    booking = (
        db.query(ParkingHistory)
        .filter(
            ParkingHistory.id == booking_id,
            ParkingHistory.user_id == current_user.id,
            ParkingHistory.status == ParkingHistoryStatus.BOOKED,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    current_time = datetime.now(IST)

    if current_time >= booking.in_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking can no longer be cancelled",
        )

    booking.status = ParkingHistoryStatus.CANCELLED

    db.commit()
    db.refresh(booking)

    return booking
