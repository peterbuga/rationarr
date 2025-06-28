import uuid
from datetime import datetime, timezone
from typing import Dict

from pydantic import BaseModel
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Uuid,
)
from sqlalchemy.sql import func

from app.db.base import Base

# from sqlalchemy import Boolean, Column, Float, Integer, String
from app.db.utc_date_time import UtcDateTime
from app.models._util import TimestampedModel


class Scraper(Base):
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    tracker_id = Column(Uuid, ForeignKey("tracker.id"), index=True)
    attribute = Column(String)
    value = Column(String)
    created_at = Column(UtcDateTime, nullable=False, default=func.now(tz=timezone.utc))
    updated_at = Column(UtcDateTime, nullable=False, default=func.now(tz=timezone.utc))


class ScraperInputModel(BaseModel):
    tracker_id: uuid.UUID
    attribute: str
    value: str


class ScraperOutputModel(TimestampedModel):
    tracker_id: uuid.UUID
    attribute: str
    value: str
    created_at: datetime


class ScraperDataOutputModel(BaseModel):
    ratio: Dict[datetime, float]
    seed: Dict[datetime, int]
    leech: Dict[datetime, int]
    hnr: Dict[datetime, int]
    # test: Optional[Dict[datetime, int]] = {}
