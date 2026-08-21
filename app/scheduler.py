from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.utils.parking import auto_cancel_expired_bookings

scheduler = BackgroundScheduler()


def scheduled_auto_cancel_job():
    db = SessionLocal()
    try:
        auto_cancel_expired_bookings(db)
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        scheduled_auto_cancel_job,
        "interval",
        minutes=5,  # Run every 5 minutes
        id="auto_cancel_bookings",
        replace_existing=True,
    )
    scheduler.start()


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
