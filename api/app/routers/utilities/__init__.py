"""Utilities domain router — selections, health, imports, exports."""
from fastapi import APIRouter

from app.routers.utilities.selections import router as selections_router

router = APIRouter(prefix="/utilities", tags=["utilities"])
router.include_router(selections_router)
