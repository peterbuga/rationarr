from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TimestampedModel(BaseModel):
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
