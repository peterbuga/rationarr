from contextlib import contextmanager
from typing import Annotated, Generator, Iterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_async_engine(str(settings.DATABASE_URI), echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# @contextmanager
# def get_db_session() -> Iterator[Session]:
#     db = AsyncSessionLocal()
#     yield db
