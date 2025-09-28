import re
import uuid
from datetime import datetime, timezone
from typing import Dict

import bitmath
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, String, Uuid
from sqlalchemy.orm import validates
from sqlalchemy.sql import func

from app.db.base import Base

# from sqlalchemy import Boolean, Column, Float, Integer, String
from app.db.utc_date_time import UtcDateTime
from app.models._util import TimestampedModel
from app.schemas.common import ScraperFields


class Scraper(Base):
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    indexer_id = Column(Uuid, ForeignKey("indexer.id"), index=True)
    attribute = Column(String)
    value = Column(String)
    created_at = Column(
        UtcDateTime, nullable=False, default=func.now(tz=timezone.utc)
    )
    updated_at = Column(
        UtcDateTime, nullable=False, default=func.now(tz=timezone.utc)
    )

    @validates("value")
    def validate_value(self, key, value):
        # convert string-storage values into bytes
        if self.attribute in [
            ScraperFields.upload.value,
            ScraperFields.download.value,
            ScraperFields.balance.value,
            ScraperFields.buffer.value,
        ]:
            if bool(re.search(r"[^0-9]", value)):
                size = bitmath.parse_string(value)
                value = str(int(size.bytes))

        return value.strip()


class ScraperInputModel(BaseModel):
    indexer_id: uuid.UUID
    attribute: str
    value: str


class ScraperOutputModel(TimestampedModel):
    indexer_id: uuid.UUID
    attribute: str
    value: str


class ScraperDataOutputModel(BaseModel):
    ratio: Dict[datetime, float] = dict()
    seed: Dict[datetime, int] = dict()
    leech: Dict[datetime, int] = dict()
    hnr: Dict[datetime, int] = dict()
    points: Dict[datetime, float] = dict()
    # download: Dict[datetime, float] = dict()
    # upload: Dict[datetime, float] = dict()
    # test: Optional[Dict[datetime, int]] = {}
