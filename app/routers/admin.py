from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.parking_history import ParkingHistoryResponse
from app.schemas.parking_space import ParkingSpaceCreate, ParkingSpaceResponse
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/parking-history", response_model=list[ParkingHistoryResponse])
def get_parking_history(
    db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    return admin_service.get_parking_history(db)


@router.get(
    "/parking-history/{vehicle_number}", response_model=list[ParkingHistoryResponse]
)
def get_vehicle_history(
    vehicle_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return admin_service.get_vehicle_history(db, vehicle_number)


@router.post(
    "/parking-spaces",
    response_model=ParkingSpaceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_parking_space(
    request: ParkingSpaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return admin_service.create_parking_space(db, request)
