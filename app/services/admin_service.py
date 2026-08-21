from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.parking_history import ParkingHistory
from app.models.parking_space import ParkingSpace
from app.schemas.parking_space import ParkingSpaceCreate
from app.utils.parking import find_parking_space


def get_parking_history(db: Session):
    return db.query(ParkingHistory).order_by(ParkingHistory.in_time.desc()).all()


def get_vehicle_history(db: Session, vehicle_number: str):
    return (
        db.query(ParkingHistory)
        .filter(ParkingHistory.vehicle_number == vehicle_number)
        .order_by(ParkingHistory.in_time.desc())
        .all()
    )


def create_parking_space(
    db: Session,
    request: ParkingSpaceCreate,
):
    existing_level = find_parking_space(db, request.level, False)

    if existing_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parking level already exists",
        )

    if request.twa < 0 or request.fwa < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of parking spaces cannot be negative",
        )

    parking_space = ParkingSpace(
        level=request.level,
        twa=request.twa,
        fwa=request.fwa,
    )

    db.add(parking_space)
    db.commit()
    db.refresh(parking_space)

    return parking_space
