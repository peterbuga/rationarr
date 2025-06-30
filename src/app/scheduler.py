import importlib
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.dependencies import get_scheduler
from app.models.tracker import Tracker


async def scheduled_crawl(tracker: Tracker):
    try:
        # TODO: check if module already loaded
        tracker_class = tracker.type.capitalize()
        module = importlib.import_module(f"app.indexers.{tracker.type}")
        tracker_instance = getattr(module, tracker_class)(**tracker.__dict__)
    except Exception as e:
        raise (f"Tracker is not supported: {tracker.type}. Err: {str(e)}")

    async with AsyncSessionLocal() as session:
        try:
            await tracker_instance.extract_info(session)
        except Exception as e:
            logging.error(f"Failed to crawl {tracker.url}: {e}")


async def start_scheduler():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Tracker).order_by(Tracker.created_at))
        trackers = result.scalars().all()

    scheduler = get_scheduler()
    for tracker in trackers:
        # if tracker.alias != 'MAM':
        #     continue
        scheduler.add_job(
            scheduled_crawl,
            max_instances=1,
            trigger="interval",
            seconds=1800,
            misfire_grace_time=30,
            kwargs={"tracker": tracker},
        )
