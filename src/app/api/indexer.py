import inspect
import re
import sys

# import logging
import httpx
from fastapi import APIRouter

# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.dependencies import DbSessionDep
from app.indexers import *
from app.indexers import base_indexer
from app.models.indexer import (
    Indexer,
    IndexerInputModel,
    IndexerListOutputModel,
    IndexerOutputModel,
)

router = APIRouter()


@router.get("/list", response_model=list[IndexerListOutputModel])
async def list_indexers():
    rationarr_indexers = {}

    def get_indexer_key(indexer_key):
        return re.sub(r"[\s\-\.]", "", indexer_key.lower())

    async with httpx.AsyncClient() as client:
        prowlarr_indexers_url = f"{settings.PROWLARR_HOST}api/v1/indexer/schema"
        response = await client.get(
            prowlarr_indexers_url,
            timeout=10,
            headers={"X-Api-Key": settings.PROWLARR_APIKEY},
        )
        response.raise_for_status()

        prowlarr_indexers = {
            get_indexer_key(indexer["definitionName"]): indexer
            for indexer in response.json()
            if indexer["protocol"] == "torrent"
            and indexer["privacy"] == "private"
        }

    # TODO: clean the hackish
    for name_idx, (name_obj, obj) in enumerate(
        inspect.getmembers(sys.modules[__name__])
    ):
        for member_name, member_obj in inspect.getmembers(obj):
            if (
                inspect.isclass(member_obj)
                and issubclass(member_obj, base_indexer.BaseIndexer)
                and member_obj != base_indexer.BaseIndexer
            ):
                indexer_key = name_obj.lower()

                if indexer_key == member_name.lower() and indexer_key in list(
                    prowlarr_indexers.keys()
                ):
                    rationarr_indexers[indexer_key] = IndexerListOutputModel(
                        **{
                            "id": name_idx,
                            "name": member_obj.name
                            or prowlarr_indexers[indexer_key]["definitionName"],
                            "alias": member_obj.alias or name_obj.upper(),
                            "url": prowlarr_indexers[indexer_key][
                                "indexerUrls"
                            ],
                        }
                    )

    return list(rationarr_indexers.values())


@router.get("", response_model=list[IndexerOutputModel])
async def get_indexers(db: DbSessionDep):
    result = await db.execute(select(Indexer).order_by(Indexer.created_at))
    indexers = result.scalars().all()

    return indexers


@router.post("", response_model=IndexerOutputModel)
async def add_indexer(indexer: IndexerInputModel, db: DbSessionDep):
    indexer_data = Indexer(**indexer.model_dump())
    db.add(indexer_data)
    await db.commit()
    await db.refresh(indexer_data)
    # print('ttt', indexer_data.__dict__, indexer_data.__mapper__)
    return indexer_data.__dict__
