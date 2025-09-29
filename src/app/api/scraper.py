import logging
import uuid

from fastapi import APIRouter
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import aggregate_order_by

from app.dependencies import DbSessionDep
from app.models import Indexer, Scraper
from app.models.scraper import ScraperDataOutputModel

router = APIRouter()


@router.get("/{id}", response_model=ScraperDataOutputModel)
async def scraped_data(id: uuid.UUID, db: DbSessionDep):
    stmt = (
        select(
            Scraper.attribute,
            func.json_object_agg(
                Scraper.created_at,
                aggregate_order_by(Scraper.value, Scraper.created_at),
            ).label("agg"),
        )
        .where(Scraper.indexer_id == id)
        .group_by(Scraper.attribute)
    )
    # logging.error(f"{stmt}")
    result = await db.execute(stmt)
    # columns = result.keys()
    # for row in result:
    #     print(dict(zip(columns, row)))
    data = dict(result.all())

    # if not data:
    #     raise HTTPException(status_code=404, detail="No data found for this endpoint")

    return ScraperDataOutputModel(**data)
