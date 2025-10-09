import importlib
import logging

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# from slugify import slugify
from sqlalchemy import func, select

from app.config import settings
from app.db import AsyncSessionLocal
from app.dependencies import SchedulerSessionDep, get_scheduler
from app.indexers.base_indexer import BaseIndexer
from app.models import Indexer, Scraper
from app.utils.flaresolverr import flarsolverr_destroy_session


async def get_indexer_instance(indexer: Indexer) -> BaseIndexer:
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
        await indexer_instance.set_db_session(session)

    return indexer_instance


async def scheduled_crawls():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Indexer)
            .where(Indexer.active.is_(True))
            .order_by(Indexer.created_at)
        )
        indexers = result.scalars().all()

    for indexer in indexers:
        logging.info(f"Gathering stats for {indexer.name}")

        try:
            indexer_instance = await get_indexer_instance(indexer)
            await indexer_instance.extract_info()
        except Exception as e:
            logging.error(f"Failed to crawl {indexer.url}: {e}")

        await flarsolverr_destroy_session(indexer.type)


async def exchange_points():
    # Get the latest `points` entries for all the indexers
    s = (
        select(
            Scraper.indexer_id,
            Scraper.value,
            Scraper.created_at,
            func.row_number()
            .over(
                partition_by=Scraper.indexer_id,
                order_by=Scraper.created_at.desc(),
            )
            .label("rn"),
        )
        # TODO: add a period-limit to avoid stale entries
        # or inactive indexers
        .where(Scraper.attribute == "points").subquery()
    ).alias("s")

    stmt = (
        select(
            s.c.indexer_id,
            Indexer.type,
            s.c.value.label("points"),
            s.c.created_at,
        )
        .join(Indexer, Indexer.id == s.c.indexer_id)
        .where(s.c.rn == 1)
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(stmt)
        indexer_points = result.mappings().all()

        for indexer_point in indexer_points:
            indexer = await session.get(
                Indexer, indexer_point.get("indexer_id")
            )
            indexer_instance = await get_indexer_instance(indexer)

            # TODO: check if last exchange_points() was run before the latest `points` entry
            # and/or trigger an extract_info() refresh after ran successfully (with some delay to allow website to update info)
            if (
                indexer.exchange_points is not None
                and float(indexer_point.points) > indexer.exchange_points
            ):
                logging.warning(
                    f"Triggered `{indexer_point.type}` for total {indexer_point.points} points, "
                    f"auth-exchange {indexer.exchange_points}"
                )

                try:
                    await indexer_instance.exchange_points(
                        total_points=float(indexer_point.get("points")),
                        target_points=indexer.exchange_points,
                    )
                except Exception as e:
                    logging.error(f"Exchange points: {str(e)}")

                await flarsolverr_destroy_session(indexer.type)


async def start_scheduler(scheduler: SchedulerSessionDep = get_scheduler()):
    scheduler.resume()

    scheduler.scheduled_job(
        id="scheduled_crawls",
        name="scheduled_crawls",
        func=scheduled_crawls,
        trigger=IntervalTrigger(seconds=settings.INTERVAL_SCRAPE),
    )

    scheduler.scheduled_job(
        id="echange_points",
        name="echange_points",
        func=exchange_points,
        trigger=CronTrigger(hour="*/6", minute=15, second=30),
        # trigger=CronTrigger(second="*/10"),
    )
