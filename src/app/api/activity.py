import logging
import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import DbSessionDep
from app.models import Indexer
from app.models.activity import Activity, ActivityOutputModel

router = APIRouter()


@router.get("", response_model=list[ActivityOutputModel])
async def get_activities(db: DbSessionDep):
    stmt = (
        select(Activity.__table__, Indexer.name.label("indexer_name"))
        .join(Indexer)
        .order_by(Activity.created_at.desc())
        .limit(500)
    )
    activities = (await db.execute(stmt)).mappings().all()

    return [ActivityOutputModel(**activity) for activity in activities]


@router.get("/{id}", response_model=ActivityOutputModel)
async def get_activity(id: uuid.UUID, db: DbSessionDep):
    stmt = (
        select(Activity.__table__, Indexer.name.label("indexer_name"))
        .join(Indexer)
        .where(Activity.id == id)
    )
    activity = (await db.execute(stmt)).mappings().first()

    return ActivityOutputModel(**activity)
