import inspect
import sys

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db

from app.indexers import *
from app.models.indexer import IndexerOutputModel


router = APIRouter()


@router.get("/", response_model=list[IndexerOutputModel])
async def get_trackers(session: AsyncSession = Depends(get_db)):
    indexers = {}
    # TODO: clean the hackish
    for name_obj, obj in inspect.getmembers(sys.modules[__name__]):
        for member_name, member_obj in inspect.getmembers(obj):
            if (
                inspect.isclass(member_obj)
                and issubclass(member_obj, base_indexer.BaseIndexer)
                and member_obj != base_indexer.BaseIndexer
            ):
                indexers[member_obj.name] = IndexerOutputModel(
                    **{
                        "name": member_obj.name,
                        "alias": member_obj.alias,
                        "url": member_obj.url,
                    }
                )

    return list(indexers.values())

