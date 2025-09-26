import uuid
from datetime import timezone
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_serializer

# from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, String, Uuid
from sqlalchemy.sql import func

from app.db.base import Base
from app.db.utc_date_time import UtcDateTime
from app.models._util import TimestampedModel


class IndexerListOutputModel(BaseModel):
    id: int
    name: str
    alias: Optional[str] = None
    url: Optional[list[HttpUrl]] = None

    class Config:
        from_attributes = True


class Indexer(Base):
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    api_key = Column(String, nullable=True)
    cookie = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    mfa_key = Column(String, nullable=True)
    created_at = Column(
        UtcDateTime, nullable=False, default=func.now(tz=timezone.utc)
    )
    updated_at = Column(
        UtcDateTime, nullable=False, default=func.now(tz=timezone.utc)
    )

    @property
    def alias(self):
        return self.type.upper()


class IndexerInputModel(BaseModel):
    name: str
    url: HttpUrl
    type: str
    api_key: Optional[str] = None
    cookie: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    mfa_key: Optional[str] = None

    @field_serializer("url", when_used="unless-none")
    def serialize_url(self, url: HttpUrl, _info):
        return str(url)


class IndexerOutputModel(TimestampedModel):
    id: str | uuid.UUID
    name: str
    url: HttpUrl
    alias: str
    active: bool = True
    api_key: Optional[str] = None
    cookie: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    mfa_key: Optional[str] = None

    class Config:
        from_attributes = True
