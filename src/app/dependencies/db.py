from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
