from fastapi import APIRouter

from app.routers.settings.accounts import router as accounts_router

router = APIRouter(prefix="/settings", tags=["settings"])
router.include_router(accounts_router)
