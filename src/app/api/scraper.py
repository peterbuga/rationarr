import logging
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.scraper import Scraper, ScraperDataOutputModel



router = APIRouter()

from sqlalchemy import select


@router.get("/{id}", response_model=ScraperDataOutputModel)
async def scraped_data(id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    stmt = (
        select(
            Scraper.attribute,
            func.json_object_agg(
                Scraper.created_at,
                aggregate_order_by(Scraper.value, Scraper.created_at),
            ).label("agg"),
        )
        .where(Scraper.tracker_id == id)
        .group_by(Scraper.attribute)
    )
    logging.error(f"{stmt}")
    result = await session.execute(stmt)
    # columns = result.keys()
    # for row in result:
    #     print(dict(zip(columns, row)))
    data = dict(result.all())

    # if not data:
    #     raise HTTPException(status_code=404, detail="No data found for this endpoint")

    return ScraperDataOutputModel(**data)
