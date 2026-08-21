from datetime import datetime

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import admin, auth, booking, parking
from app.utils import datetime
from app.scheduler import start_scheduler, shutdown_scheduler
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(lifespan=lifespan)

app.json_encoders = {datetime: datetime.custom_datetime_encoder}

app.include_router(auth.router)
app.include_router(parking.router)
app.include_router(booking.router)
app.include_router(admin.router)

Base.metadata.create_all(bind=engine)
