from fastapi import APIRouter

from app.api.indexer import router as indexer_router
from app.api.job import router as job_router
from app.api.scraper import router as scraper_router

api_router = APIRouter(prefix="/api")

api_router.include_router(indexer_router, prefix="/indexer", tags=[])
api_router.include_router(scraper_router, prefix="/scraper", tags=[])
api_router.include_router(job_router, prefix="/job", tags=[])

try:
    from app.api.test import router as test_router

    api_router.include_router(test_router, prefix="/test", tags=[])
except:
    pass
