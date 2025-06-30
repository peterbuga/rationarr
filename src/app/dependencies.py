from typing import Annotated

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(
        # jobstores={'default': MemoryJobStore()},
        timezone="UTC"
    )
    scheduler.start()

    return scheduler


# Singleton instance
scheduler_instance: AsyncIOScheduler = create_scheduler()


def get_scheduler() -> AsyncIOScheduler:
    return scheduler_instance


SchedulerSessionDep = Annotated[AsyncIOScheduler, Depends(get_scheduler)]


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
