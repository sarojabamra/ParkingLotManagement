from datetime import datetime

from app.constants import IST


def custom_datetime_encoder(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt_ist_aware = IST.localize(dt)
    else:
        dt_ist_aware = dt.astimezone(IST)
    return dt_ist_aware.isoformat(sep=" ", timespec="milliseconds")
