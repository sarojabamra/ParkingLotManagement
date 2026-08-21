from sqlalchemy import Column, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.constants import ParkingLotStatus, ParkingType
from app.database import Base


class Parking(Base):
    __tablename__ = "parking"

    __table_args__ = (
        UniqueConstraint("level", "lot_number", name="uq_parking_level_lot"),
    )

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, ForeignKey("parking_spaces.level"), nullable=False)
    lot_number = Column(Integer, nullable=False)
    type = Column(Enum(ParkingType), nullable=False)

    status = Column(
        Enum(ParkingLotStatus), nullable=False, default=ParkingLotStatus.AVAILABLE
    )

    parking_space = relationship("ParkingSpace", back_populates="parking_lots")

    parking_history = relationship("ParkingHistory", back_populates="parking")
