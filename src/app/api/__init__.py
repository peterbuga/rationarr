from fastapi import APIRouter

from app.api.activity import router as activity_router
from app.api.health import router as health_router
from app.api.indexer import router as indexer_router
from app.api.job import router as job_router
from app.api.scraper import router as scraper_router

api_router = APIRouter(prefix="/api")

api_router.include_router(indexer_router, prefix="/indexer", tags=[])
api_router.include_router(scraper_router, prefix="/scraper", tags=[])
api_router.include_router(activity_router, prefix="/activity", tags=[])
api_router.include_router(job_router, prefix="/job", tags=[])
api_router.include_router(health_router, prefix="/health", tags=[])

try:
    from app.api.test import router as test_router

    api_router.include_router(test_router, prefix="/test", tags=[])
except Exception:
    pass

# api_router.include_router(zoc.router, prefix="/zoc", tags=[Tags.zoc])
# api_router.include_router(share.router, prefix="/share", tags=[Tags.share])
# api_router.include_router(account.router, prefix="/account", tags=[Tags.account])
# api_router.include_router(quiz.router, prefix="/quiz", tags=[Tags.quiz])


# system_deps = [Depends(PermissionsValidator([KnownScopes.SYSTEM.value]))]
# system_tags = [Tags.system]
# system_business_tags = [Tags.system_business]
# system_affiliate_tags = [Tags.system_affiliate]

# api_router.include_router(db_utils.router, prefix="/system/db-utils", tags=system_tags, dependencies=system_deps)
# api_router.include_router(admin_affiliate_account.router, prefix="/system/affiliate", tags=system_affiliate_tags, dependencies=system_deps)
# api_router.include_router(admin_zoc.router, prefix="/system/zoc", tags=system_tags, dependencies=system_deps)
# api_router.include_router(admin_quiz.router, prefix="/system/quiz", tags=system_tags, dependencies=system_deps)
# api_router.include_router(admin_business.router, prefix="/system/b2b", tags=system_business_tags, dependencies=system_deps)
# api_router.include_router(logs.router, prefix="/system/logs", tags=system_tags, dependencies=system_deps)
# api_router.include_router(transcript.router, prefix="/system/transcript", tags=system_tags, dependencies=system_deps)
# api_router.include_router(translate.router, prefix="/system/translate", tags=system_tags, dependencies=system_deps)
# api_router.include_router(system_user.router, prefix="/system/user", tags=system_tags, dependencies=system_deps)
