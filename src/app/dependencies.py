from typing import Annotated

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import AsyncSessionLocal


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(
        jobstores={
            "default": SQLAlchemyJobStore(
                tablename="job",
                url=str(settings.DATABASE_URI).replace("+asyncpg", ""),
            )
        },
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": None,
        },
        timezone="UTC",
    )
    scheduler.start(True)
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
