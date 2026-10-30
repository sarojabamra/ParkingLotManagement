from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import admin, auth, booking, parking
from app.scheduler import shutdown_scheduler, start_scheduler
from app.utils.datetime import custom_datetime_encoder


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(lifespan=lifespan)

app.json_encoders = {datetime: custom_datetime_encoder}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(parking.router)
app.include_router(booking.router)
app.include_router(admin.router)

Base.metadata.create_all(bind=engine)
