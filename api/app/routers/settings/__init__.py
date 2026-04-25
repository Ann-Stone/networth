from fastapi import APIRouter

from app.routers.settings.accounts import router as accounts_router
from app.routers.settings.codes import router as codes_router
from app.routers.settings.sub_codes import router as sub_codes_router

router = APIRouter(prefix="/settings", tags=["settings"])
router.include_router(accounts_router)
router.include_router(codes_router)
router.include_router(sub_codes_router)
