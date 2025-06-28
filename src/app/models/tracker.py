import uuid
from datetime import timezone
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_serializer
from sqlalchemy import Column, String, Uuid

# from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.db.utc_date_time import UtcDateTime
from app.models._util import TimestampedModel


class Tracker(Base):
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    alias = Column(String, nullable=True)
    url = Column(String)
    type = Column(String)
    alias = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    cookie = Column(String, nullable=True)
    created_at = Column(UtcDateTime, nullable=False, default=func.now(tz=timezone.utc))
    updated_at = Column(UtcDateTime, nullable=False, default=func.now(tz=timezone.utc))


class TrackerInputModel(BaseModel):
    name: str
    alias: Optional[str] = None
    url: HttpUrl
    type: str
    api_key: Optional[str] = None
    cookie: Optional[str] = None

    @field_serializer("url", when_used="unless-none")
    def serialize_url(self, url: HttpUrl, _info):
        return str(url)


class TrackerOutputModel(TimestampedModel):
    id: str | uuid.UUID
    name: str
    alias: Optional[str] = None
    url: HttpUrl
    type: str
    api_key: Optional[str] = None
    cookie: Optional[str] = None

    class Config:
        from_attributes = True
