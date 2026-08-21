from sqlalchemy import Column, Integer

# from sqlalchemy.orm import relationship
from app.database import Base


class ParkingSpace(Base):
    __tablename__ = "parking_spaces"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, unique=True, nullable=False)
    twa = Column(Integer, nullable=False)
    fwa = Column(Integer, nullable=False)

    # parking_lots = relationship("Parking", back_populates="parking_space")
