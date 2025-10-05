import uuid
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_serializer

# from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String, Uuid

from app.db.base import Base
from app.models._util import TimestampedModel


class IndexerListOutputModel(BaseModel):
    id: int
    name: str
    type: str
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
    exchange_points = Column(Integer, nullable=True)

    @property
    def alias(self):
        return self.type.upper()


class IndexerInputModel(BaseModel):
    name: str
    url: HttpUrl
    type: str
    active: Optional[bool] = True
    api_key: Optional[str] = None
    cookie: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    mfa_key: Optional[str] = None
    exchange_points: Optional[int] = None

    @field_serializer("url", when_used="unless-none")
    def serialize_url(self, url: HttpUrl, _info):
        return str(url)


class IndexerOutputModel(TimestampedModel):
    id: str | uuid.UUID
    name: str
    url: HttpUrl
    alias: Optional[str] = None
    type: str
    active: bool = True
    api_key: Optional[str] = None
    cookie: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    mfa_key: Optional[str] = None
    exchange_points: Optional[int] = None

    class Config:
        from_attributes = True
