from datetime import timezone
from typing import Any

from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative
from sqlalchemy.sql import func

from app.db.utc_date_time import UtcDateTime


class SerializerMixin:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@as_declarative()
class Base(SerializerMixin):
    id: Any
    __name__: str

    created_at = Column(
        UtcDateTime, nullable=False, default=func.now(tz=timezone.utc)
    )
    updated_at = Column(
        UtcDateTime, nullable=False, default=func.now(tz=timezone.utc)
    )

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
