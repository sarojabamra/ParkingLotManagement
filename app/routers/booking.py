from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.parking_history import (
    BookingCreate,
    BookingResponse,
)
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(
    request: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return booking_service.create_booking(db, request, current_user)


@router.delete("/{booking_id}", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return booking_service.cancel_booking(db, booking_id, current_user)


@router.get("/", response_model=list[BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return booking_service.get_my_bookings(db, current_user)
