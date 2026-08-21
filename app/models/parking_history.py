from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.constants import ParkingHistoryStatus, ParkingType
from app.database import Base


class ParkingHistory(Base):
    __tablename__ = "parking_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level = Column(Integer, nullable=False)
    type = Column(Enum(ParkingType), nullable=False)
    vehicle_number = Column(String, nullable=False)
    lot = Column(Integer, nullable=False)
    in_time = Column(DateTime, nullable=False)
    scheduled_out_time = Column(DateTime, nullable=True)
    out_time = Column(DateTime, nullable=True)
    fee = Column(Float, nullable=True)
    status = Column(
        Enum(ParkingHistoryStatus), nullable=False, default=ParkingHistoryStatus.ACTIVE
    )

    user = relationship("User", back_populates="parking_history")
