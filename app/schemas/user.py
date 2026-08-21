from pydantic import BaseModel, ConfigDict

from app.constants import UserRole


class UserCreate(BaseModel):
    name: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    name: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
