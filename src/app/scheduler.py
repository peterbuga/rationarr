import importlib
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.dependencies import get_scheduler
from app.models.indexer import Indexer


async def scheduled_crawl(indexer: Indexer):
    try:
        # TODO: check if module already loaded
        indexer_class = indexer.type.capitalize()
        module = importlib.import_module(f"app.indexers.{indexer.type}")
        indexer_instance = getattr(module, indexer_class)(**indexer.__dict__)
    except Exception as e:
        raise Exception(
            f"Indexer is not supported: {indexer.type}. Err: {str(e)}"
        )

    async with AsyncSessionLocal() as session:
        try:
            await indexer_instance.extract_info(session)
        except Exception as e:
            logging.error(f"Failed to crawl {indexer.url}: {e}")


async def start_scheduler():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Indexer)
            .where(Indexer.active.is_(True))
            .order_by(Indexer.created_at)
        )
        indexers = result.scalars().all()

    scheduler = get_scheduler()
    for indexer in indexers:
        # if tracker.alias != 'MAM':
        #     continue
        scheduler.add_job(
            scheduled_crawl,
            max_instances=1,
            trigger="interval",
            seconds=1800,
            misfire_grace_time=30,
            kwargs={"indexer": indexer},
        )
