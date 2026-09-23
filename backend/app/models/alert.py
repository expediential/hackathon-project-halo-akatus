from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.models.incident import utcnow


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: f"ALT-{uuid4().hex[:12].upper()}")
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.incident_id"), index=True)
    alert_type: Mapped[str] = mapped_column(String(32), index=True)
    severity: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
