import datetime

from sqlalchemy.types import DateTime, TypeDecorator


class UtcDateTime(TypeDecorator):
    """Almost equivalent to :class:`~sqlalchemy.types.DateTime` with
    ``timezone=False`` option, but it differs from that by:
    - Inspired by https://github.com/spoqa/sqlalchemy-utc
    - We do not add the timezone in database
    - We assume datetime is stored in UTC in DB and attach UTC when reading from DB
    - Never silently take naive :class:`~datetime.datetime`, instead it
      always raise :exc:`ValueError` unless time zone aware value.
    - :class:`~datetime.datetime` value's :attr:`~datetime.datetime.tzinfo`
      is always converted to UTC.
    - Unlike SQLAlchemy's built-in :class:`~sqlalchemy.types.DateTime`,
      it never return naive :class:`~datetime.datetime`, but time zone
      aware value, even with SQLite or MySQL.

    """

    impl = DateTime(timezone=False)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, datetime.datetime):
                raise TypeError(
                    "expected datetime.datetime, not " + repr(value)
                )
            elif value.tzinfo is None:
                raise ValueError("naive datetime is disallowed")
            return value.astimezone(datetime.timezone.utc)

    def process_result_value(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=datetime.timezone.utc)
            else:
                value = value.astimezone(datetime.timezone.utc)
        return value
