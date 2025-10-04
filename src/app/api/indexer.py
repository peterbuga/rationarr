import inspect
import re
import sys
import uuid

# import logging
import httpx
from fastapi import APIRouter
from sqlalchemy import select, delete

from app.config import settings
from app.dependencies import DbSessionDep
from app.indexers import *  # noqa: F403
from app.indexers import base_indexer
from app.models.indexer import (
    Indexer,
    IndexerInputModel,
    IndexerListOutputModel,
    IndexerOutputModel,
)
from app.utils.url import build_url

router = APIRouter()


async def get_prowlarr_indexers_list():
    def get_indexer_key(indexer_key):
        return re.sub(r"[\s\-\.]", "", indexer_key.lower())

    async with httpx.AsyncClient() as client:
        prowlarr_indexers_url = build_url(
            settings.PROWLARR_HOST, path="/api/v1/indexer/schema"
        )
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
        prowlarr_indexer_keys = [
            "indexerUrls",
            "legacyUrls",
            "definitionName",
            "description",
            "name",
        ]
        prowlarr_indexers = {
            indexer_key: {key: indexer[key] for key in prowlarr_indexer_keys}
            for indexer_key, indexer in prowlarr_indexers.items()
        }
        return prowlarr_indexers


@router.get("/prowlarr")
async def get_prowlarr_indexers():
    return await get_prowlarr_indexers_list()


@router.get("/list", response_model=list[IndexerListOutputModel])
async def list_indexers():
    rationarr_indexers = {}
    prowlarr_indexers = await get_prowlarr_indexers_list()
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
                            or prowlarr_indexers[indexer_key]["name"].replace('(API)','').strip(),
                            "alias": member_obj.alias or name_obj.upper(),
                            "type": indexer_key,
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

@router.delete("/{id}", status_code=204)
async def remove_event(id: uuid.UUID, db: DbSessionDep):
    # result = await IndexerService.delete_events([event_id])
    stmt = delete(Indexer).where(Indexer.id == id)
    await db.execute(stmt)
    await db.commit()

    return None
