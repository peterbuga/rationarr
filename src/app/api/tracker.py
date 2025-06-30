from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import DbSessionDep
from app.models.tracker import Tracker, TrackerInputModel, TrackerOutputModel

router = APIRouter()


from sqlalchemy import select


@router.get("", response_model=list[TrackerOutputModel])
async def get_trackers(db: DbSessionDep):
    result = await db.execute(select(Tracker).order_by(Tracker.created_at))
    trackers = result.scalars().all()
    return trackers


@router.post("", response_model=TrackerOutputModel)
async def add_tracker(tracker: TrackerInputModel, db: DbSessionDep):
    tracker_data = Tracker(**tracker.model_dump())
    db.add(tracker_data)
    await db.commit()
    await db.refresh(tracker_data)
    # print('ttt', tracker_data.__dict__, tracker_data.__mapper__)
    return tracker_data.__dict__


# @router.get("/endpoints", response_model=list[EndpointInfo])
# async def list_endpoints():
#     config = load_config()
#     return [EndpointInfo(url=ep.url) for ep in config.endpoints]
