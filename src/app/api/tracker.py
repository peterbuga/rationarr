from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.tracker import Tracker, TrackerInputModel, TrackerOutputModel



router = APIRouter()


from sqlalchemy import select


@router.get("/", response_model=list[TrackerOutputModel])
async def get_trackers(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Tracker).order_by(Tracker.created_at))
    trackers = result.scalars().all()
    return trackers


@router.post("/", response_model=TrackerOutputModel)
async def add_tracker(
    tracker: TrackerInputModel, session: AsyncSession = Depends(get_db)
):
    tracker_data = Tracker(**tracker.model_dump())
    session.add(tracker_data)
    await session.commit()
    await session.refresh(tracker_data)
    # print('ttt', tracker_data.__dict__, tracker_data.__mapper__)
    return tracker_data.__dict__

