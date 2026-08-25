from datetime import datetime

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

    if in_time.tzinfo is None:
        in_time = IST.localize(in_time)
    else:
        in_time = in_time.astimezone(IST)

    if out_time.tzinfo is None:
        out_time = IST.localize(out_time)
    else:
        out_time = out_time.astimezone(IST)

    if scheduled_out_time:
        if scheduled_out_time.tzinfo is None:
            scheduled_out_time = IST.localize(scheduled_out_time)
        else:
            scheduled_out_time = scheduled_out_time.astimezone(IST)

    regular_hours_billed = (out_time - in_time).total_seconds() / 3600

    if scheduled_out_time and out_time > scheduled_out_time:
        regular_hours_billed = (scheduled_out_time - in_time).total_seconds() / 3600

    if parking_type == ParkingType.TW:
        regular_fee = regular_hours_billed * HOURLY_FEE_TWO_WHEELER
        hourly_rate = HOURLY_FEE_TWO_WHEELER
    else:
        regular_fee = regular_hours_billed * HOURLY_FEE_FOUR_WHEELER
        hourly_rate = HOURLY_FEE_FOUR_WHEELER

    total_fee = regular_fee

    if scheduled_out_time and out_time > scheduled_out_time:
        late_duration = out_time - scheduled_out_time
        late_hours = late_duration.total_seconds() / 3600
        late_fee = late_hours * hourly_rate * LATE_FEE_HOURLY_MULTIPLIER
        total_fee += late_fee

    return round(total_fee, 2)
