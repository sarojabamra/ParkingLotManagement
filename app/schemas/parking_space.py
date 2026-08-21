from pydantic import BaseModel, ConfigDict, Field


class ParkingSpaceCreate(BaseModel):
    level: int = Field(gt=0)
    twa: int = Field(ge=0)
    fwa: int = Field(ge=0)


class ParkingSpaceResponse(BaseModel):
    id: int
    level: int
    twa: int
    fwa: int

    model_config = ConfigDict(from_attributes=True)


class AdminAvailabilityResponse(BaseModel):
    level: int
    two_wheeler_available: int
    four_wheeler_available: int


class PublicAvailabilityResponse(BaseModel):
    level: int
    two_wheeler_available: bool
    four_wheeler_available: bool
