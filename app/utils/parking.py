import random
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.constants import ParkingHistoryStatus, ParkingType, IST

from app.models.parking_history import ParkingHistory
from app.models.parking_space import ParkingSpace
from app.models.user import User


def find_parking_space(
    db: Session, level: int, raiseException: bool = True
) -> ParkingSpace:
    parking_space = db.query(ParkingSpace).filter(ParkingSpace.level == level).first()

    if not parking_space and raiseException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking level not found",
        )

    return parking_space


def get_parking_lots_in_level(
    db: Session, level: int, parking_type: ParkingType
) -> list[int]:
    parking_space = find_parking_space(db, level)
    if parking_type == ParkingType.TW:
        total_slots = parking_space.twa
    else:
        total_slots = parking_space.fwa

    return list(range(1, total_slots + 1))


def get_occupied_lots(
    db: Session, level: int, parking_type: ParkingType, current_time: datetime
) -> set[int]:
    occupied_history = (
        db.query(ParkingHistory)
        .filter(
            ParkingHistory.level == level,
            ParkingHistory.type == parking_type,
            ParkingHistory.status == ParkingHistoryStatus.ACTIVE,
            ParkingHistory.in_time <= current_time,
            (ParkingHistory.out_time == None)
            | (ParkingHistory.out_time > current_time),
        )
        .all()
    )
    return {history.lot for history in occupied_history}


def get_booked_lots(
    db: Session,
    level: int,
    parking_type: ParkingType,
    start_time: datetime,
    end_time: datetime,
) -> set[int]:
    booked_history = (
        db.query(ParkingHistory)
        .filter(
            ParkingHistory.level == level,
            ParkingHistory.type == parking_type,
            ParkingHistory.status == ParkingHistoryStatus.BOOKED,
            # For a booking to conflict, its start must be before our end
            # AND its end must be after our start
            ParkingHistory.in_time < end_time,
            ParkingHistory.scheduled_out_time > start_time,
        )
        .all()
    )
    return {history.lot for history in booked_history}


def get_available_lots(
    db: Session,
    level: int,
    parking_type: ParkingType,
    start_time: datetime,
    end_time: datetime,
    error_detail: str = "No parking lots available for the requested time",  # Added default error
) -> list[int]:
    all_lots_in_level = get_parking_lots_in_level(db, level, parking_type)

    # Lots currently occupied (active parking) that conflict with the booking time
    occupied_conflict_lots = (
        db.query(ParkingHistory.lot)
        .filter(
            ParkingHistory.level == level,
            ParkingHistory.type == parking_type,
            ParkingHistory.status == ParkingHistoryStatus.ACTIVE,
            # For an active session to conflict, its in_time must be before our end
            # AND its out_time (or current time if None) must be after our start
            ParkingHistory.in_time < end_time,
            (ParkingHistory.out_time == None) | (ParkingHistory.out_time > start_time),
        )
        .all()
    )
    occupied_conflict_lots = {lot for (lot,) in occupied_conflict_lots}

    # Lots already booked that conflict with the new booking time
    booked_conflict_lots = get_booked_lots(
        db,
        level,
        parking_type,
        start_time,
        end_time,
    )

    conflicting_lots = occupied_conflict_lots.union(booked_conflict_lots)

    available_lots = [lot for lot in all_lots_in_level if lot not in conflicting_lots]

    if not available_lots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        )
    return available_lots


def decrease_parking_availability(
    parking_space: ParkingSpace, parking_type: ParkingType
) -> None:
    if parking_type == ParkingType.TW:
        parking_space.twa -= 1
    else:
        parking_space.fwa -= 1


def increase_parking_availability(
    parking_space: ParkingSpace, parking_type: ParkingType
) -> None:
    if parking_type == ParkingType.TW:
        parking_space.twa += 1
    else:
        parking_space.fwa += 1


def select_random_lot(parking_lots: list[int]) -> int:
    if not parking_lots:
        raise ValueError("No parking lots available")

    return random.choice(parking_lots)


def check_vehicle_active_parking_session(
    db: Session, vehicle_number: str
) -> ParkingHistory | None:
    return (
        db.query(ParkingHistory)
        .filter(
            ParkingHistory.vehicle_number == vehicle_number,
            ParkingHistory.status == ParkingHistoryStatus.ACTIVE,
        )
        .first()
    )


def validate_booking_time(current_time, booking):
    if current_time < booking.in_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking time has not started yet",
        )
    if booking.scheduled_out_time and current_time >= booking.scheduled_out_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking has already expired",
        )


def activate_booking(
    db: Session,
    booking: ParkingHistory,
    request: Any,
    current_time: datetime,
) -> ParkingHistory:
    validate_booking_time(current_time, booking)

    # Check if the originally booked lot is available
    occupied_lots = get_occupied_lots(
        db,
        request.level,
        request.type,
        current_time,
    )

    booked_conflict_lots = get_booked_lots(
        db,
        request.level,
        request.type,
        booking.in_time,
        booking.scheduled_out_time,
    )

    if booking.lot in occupied_lots or booking.lot in booked_conflict_lots:
        # Original booked lot is unavailable, find alternative
        # (worst case if the vehicle which locked the lot before the booking overstays)
        alternative_available_lots = get_available_lots(
            db=db,
            level=request.level,
            parking_type=request.type,
            start_time=current_time,
            end_time=booking.scheduled_out_time,
            error_detail=(
                f"Your booked parking lot {booking.lot} is occupied, "
                "and no suitable alternative lot is available "
                "for your remaining booking duration."
            ),
        )

    booking.lot = select_random_lot(alternative_available_lots)

    booking.status = ParkingHistoryStatus.ACTIVE

    return booking


def create_immediate_parking(
    db: Session,
    request,
    current_user: User,
    current_time: datetime,
) -> ParkingHistory:

    available_lots = get_available_lots(
        db,
        request.level,
        request.type,
        current_time,
        current_time + timedelta(hours=1),
        error_detail="No parking lots available for immediate parking.",
    )

    assigned_lot = select_random_lot(available_lots)

    parking_record = ParkingHistory(
        user_id=current_user.id,
        level=request.level,
        type=request.type,
        vehicle_number=request.vehicle_number,
        lot=assigned_lot,
        in_time=current_time,
        scheduled_out_time=None,
        out_time=None,
        fee=None,
        status=ParkingHistoryStatus.ACTIVE,
    )

    return parking_record
