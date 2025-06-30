from fastapi import APIRouter, Depends

from app.api.indexer import router as indexer_router
from app.api.scraper import router as scraper_router
from app.api.tracker import router as tracker_router

api_router = APIRouter(prefix="/api")

api_router.include_router(tracker_router, prefix="/tracker", tags=[])
api_router.include_router(indexer_router, prefix="/indexer", tags=[])
api_router.include_router(scraper_router, prefix="/scraper", tags=[])

