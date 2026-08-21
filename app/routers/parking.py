from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.parking_history import (
    ParkingHistoryResponse,
    ParkingLockRequest,
    ParkingLockResponse,
    ParkingUnlockRequest,
    ParkingUnlockResponse,
)
from app.services import parking_service

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.get("/availability")
def get_availability(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return parking_service.get_availability(db, current_user)


@router.get("/history", response_model=list[ParkingHistoryResponse])
def get_my_parking_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return parking_service.get_my_parking_history(db, current_user)


# lock/assign lot
@router.post("/lock", response_model=ParkingLockResponse, status_code=201)
def lock_parking(
    request: ParkingLockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return parking_service.lock_parking(request, db, current_user)


# unlock/unassign lot
@router.post("/unlock", response_model=ParkingUnlockResponse)
def unlock_parking(
    request: ParkingUnlockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Corrected order of arguments: db first, then request
    return parking_service.unlock_parking(db, request, current_user)
