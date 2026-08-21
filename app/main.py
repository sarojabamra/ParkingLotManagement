from datetime import datetime

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import admin, auth, booking, parking
from app.utils import datetime

app = FastAPI()

app.json_encoders = {datetime: datetime.custom_datetime_encoder}

app.include_router(auth.router)
app.include_router(parking.router)
app.include_router(booking.router)
app.include_router(admin.router)

Base.metadata.create_all(bind=engine)
