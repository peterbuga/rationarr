import uuid

from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, String, Uuid

from app.db.base import Base
from app.models._util import TimestampedModel


class Activity(Base):
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    indexer_id = Column(Uuid, ForeignKey("indexer.id"), index=True)
    activity = Column(String)


class ActivityInputModel(BaseModel):
    indexer_id: uuid.UUID
    activity: str


class ActivityOutputModel(TimestampedModel):
    id: uuid.UUID
    indexer_id: uuid.UUID
    indexer_name: str
    activity: str
