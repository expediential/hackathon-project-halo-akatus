from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column("incident_id", String(40), primary_key=True, default=lambda: f"INC-{uuid4().hex[:12].upper()}")
    incident_type: Mapped[str] = mapped_column(String(32), default="UNKNOWN", index=True)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    priority: Mapped[str] = mapped_column(String(16), default="LOW", index=True)
    status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED", index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_facts: Mapped[list] = mapped_column(JSON, default=list)
    uncertain_facts: Mapped[list] = mapped_column(JSON, default=list)
    contradictions: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    last_report_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    reports = relationship("EmergencyReport", back_populates="incident")
    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan")


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id: Mapped[str] = mapped_column("event_id", String(40), primary_key=True, default=lambda: f"EVT-{uuid4().hex[:12].upper()}")
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.incident_id"), index=True)
    event_type: Mapped[str] = mapped_column(String(64))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    description: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(64), default="SYSTEM")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    incident = relationship("Incident", back_populates="events")
