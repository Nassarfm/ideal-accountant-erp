from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.health import HealthResponse


def build_health_response(db: Session) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.app_env,
        database="connected",
    )
