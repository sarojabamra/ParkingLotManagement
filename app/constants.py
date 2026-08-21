from enum import Enum

import pytz


class ParkingType(str, Enum):
    TW = "TW"
    FW = "FW"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    PUBLIC = "PUBLIC"


class ParkingHistoryStatus(str, Enum):
    BOOKED = "BOOKED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


IST = pytz.timezone("Asia/Kolkata")
