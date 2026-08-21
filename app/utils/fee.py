from datetime import datetime, timedelta
from app.constants import ParkingType, IST

HOURLY_FEE_TWO_WHEELER = 10
HOURLY_FEE_FOUR_WHEELER = 20
LATE_FEE_HOURLY_MULTIPLIER = 1.5


def calculate_parking_fee(
    parking_type: ParkingType,
    in_time: datetime,
    out_time: datetime,
    scheduled_out_time: datetime | None = None,
) -> float:

    regular_hours_billed = (out_time - in_time).total_seconds() / 3600
    if scheduled_out_time and out_time < scheduled_out_time:
        # If exiting before scheduled, only charge until actual exit time
        regular_hours_billed = (out_time - in_time).total_seconds() / 3600
    elif scheduled_out_time and out_time > scheduled_out_time:
        # If exiting after scheduled, calculate fee for scheduled period and then late fee for extended period
        regular_hours_billed = (scheduled_out_time - in_time).total_seconds() / 3600
    if parking_type == ParkingType.TW:
        regular_fee = regular_hours_billed * HOURLY_FEE_TWO_WHEELER
        hourly_rate = HOURLY_FEE_TWO_WHEELER
    else:
        regular_fee = regular_hours_billed * HOURLY_FEE_FOUR_WHEELER
        hourly_rate = HOURLY_FEE_FOUR_WHEELER

    total_fee = regular_fee

    # Calculate late fee
    if scheduled_out_time and out_time > scheduled_out_time:
        late_duration = out_time - scheduled_out_time
        late_hours = late_duration.total_seconds() / 3600
        late_fee = late_hours * hourly_rate * LATE_FEE_HOURLY_MULTIPLIER
        total_fee += late_fee
    return round(total_fee, 2)
