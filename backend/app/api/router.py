from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.audio import router as audio_router
from app.api.analysis import router as analysis_router
from app.api.history import router as history_router
from app.api.reports import router as reports_router
from app.api.health import router as health_router

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(audio_router)
api_router.include_router(analysis_router)
api_router.include_router(history_router)

# Mount both /report and /reports for clinical reports
api_router.include_router(reports_router, prefix="/report")
api_router.include_router(reports_router, prefix="/reports")
