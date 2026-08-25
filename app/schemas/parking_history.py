from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import ParkingHistoryStatus, ParkingType


class ParkingLockRequest(BaseModel):
    vehicle_number: str = Field(min_length=1)
    level: int = Field(gt=0)
    type: ParkingType


class ParkingLockResponse(BaseModel):
    vehicle_number: str
    type: ParkingType
    level: int
    lot: int
    locking_time: datetime
    user_id: int


class ParkingUnlockRequest(BaseModel):
    vehicle_number: str = Field(min_length=1)
    level: int = Field(gt=0)
    lot: int = Field(gt=0)


class ParkingUnlockResponse(BaseModel):
    vehicle_number: str
    lot: int
    locking_time: datetime
    unlocking_time: datetime
    parking_fee: float
    user_id: int


class BookingCreate(BaseModel):
    vehicle_number: str = Field(min_length=1, example="MP09 8282")
    level: int = Field(gt=0, example=2)
    type: ParkingType = Field(example=ParkingType.TW)
    start_time: datetime = Field(example="2026-08-25T11:59:45.895+05:30")
    end_time: datetime = Field(example="2026-08-25T14:50:45.895+05:30")


class BookingResponse(BaseModel):
    id: int
    vehicle_number: str
    level: int
    type: ParkingType
    lot: int
    start_time: datetime = Field(alias="in_time")
    end_time: datetime | None = Field(alias="scheduled_out_time")
    status: ParkingHistoryStatus
    user_id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ParkingHistoryResponse(BaseModel):
    id: int
    user_id: int
    level: int
    type: ParkingType
    vehicle_number: str
    lot: int
    in_time: datetime
    out_time: datetime | None
    fee: float | None
    status: ParkingHistoryStatus

    model_config = ConfigDict(from_attributes=True)
