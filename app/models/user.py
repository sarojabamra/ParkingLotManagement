from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.constants import UserRole
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    parking_history = relationship("ParkingHistory", back_populates="user")
