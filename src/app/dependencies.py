from fastapi import Depends
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Annotated


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
