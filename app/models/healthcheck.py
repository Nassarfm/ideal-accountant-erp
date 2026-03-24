from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HealthCheck(Base):
    __tablename__ = "health_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service_name: Mapped[str] = mapped_column(String(100), default="erp-backend")
    status: Mapped[str] = mapped_column(String(20), default="ok")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
