from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.incident import utcnow


class EmergencyReport(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column("report_id", String(40), primary_key=True, default=lambda: f"RPT-{uuid4().hex[:12].upper()}")
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    description: Mapped[str] = mapped_column(Text)
    incident_type: Mapped[str] = mapped_column(String(32), default="UNKNOWN", index=True)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED")
    priority: Mapped[str] = mapped_column(String(16), default="LOW")
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.incident_id"), index=True)
    is_outdated: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence: Mapped[list] = mapped_column(JSON, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    extraction: Mapped[dict] = mapped_column(JSON, default=dict)
    duplicate_similarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    incident = relationship("Incident", back_populates="reports")
