# import logging
from datetime import datetime, timedelta

from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import APIRouter

# from app.dependencies import DbSessionDep
from app.dependencies import SchedulerSessionDep
from app.models.indexer import Indexer

router = APIRouter()


def safe_serialize(obj):
    """Ensure object is JSON serializable."""
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, timedelta):
        return {
            "days": obj.days,
            "seconds": obj.seconds,
            "microseconds": obj.microseconds,
            "total_seconds": obj.total_seconds(),
        }
    if isinstance(obj, (list, tuple)):
        return [safe_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): safe_serialize(v) for k, v in obj.items()}
    if isinstance(obj, Indexer):
        return {str(k): safe_serialize(v) for k, v in obj.to_dict().items()}
    return str(obj)  # fallback


def trigger_to_dict(trigger):
    if isinstance(trigger, CronTrigger):
        return {
            "type": "cron",
            "fields": {f.name: str(f) for f in trigger.fields},
        }
    elif isinstance(trigger, IntervalTrigger):
        return {
            "type": "interval",
            "interval": safe_serialize(
                trigger.interval
            ),  # timedelta serialized
            "start_date": safe_serialize(trigger.start_date),
            "end_date": safe_serialize(trigger.end_date),
            "timezone": str(trigger.timezone),
        }
    elif isinstance(trigger, DateTrigger):
        return {
            "type": "date",
            "run_date": safe_serialize(trigger.run_date),
            "timezone": str(trigger.timezone),
        }
    else:
        return {"type": trigger.__class__.__name__, "repr": str(trigger)}


def job_to_dict(job: Job) -> dict:
    return {
        "id": job.id,
        "name": job.name,
        "next_run_time": safe_serialize(job.next_run_time),
        "trigger": trigger_to_dict(job.trigger),
        "func_ref": job.func_ref,
        "args": safe_serialize(job.args),
        "kwargs": safe_serialize(job.kwargs),
        "misfire_grace_time": job.misfire_grace_time,
        "coalesce": job.coalesce,
        "max_instances": job.max_instances,
    }


# for testing
@router.get("")
async def get_jobs(scheduler: SchedulerSessionDep):
    jobs = scheduler.get_jobs()

    # return {"scheduled_jobs": [job.id for job in jobs]}
    return [job_to_dict(job) for job in jobs]
