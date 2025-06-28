from fastapi import FastAPI, Depends

from app.api import api_router
from app.scheduler import start_scheduler
from app.dependencies import SchedulerSessionDep

app = FastAPI(
    title="Rationarr",
    description="API-only FastAPI app for scheduled data crawling from configured websites.",
    version="0.1.0",
)

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    await start_scheduler()

@app.get("/")
@app.get("/health")
async def root():
    return {"message": "Rationarr API is running."}

@app.get("/jobs")
async def get_jobs(scheduler: SchedulerSessionDep):
    jobs = scheduler.get_jobs()

    return {"scheduled_jobs": [job.id for job in jobs]}
