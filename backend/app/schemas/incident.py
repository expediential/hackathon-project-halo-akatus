from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.enums import IncidentType, InformationStatus, Priority
from app.schemas.common import Location


class IncidentRead(BaseModel):
    incident_id: str
    type: IncidentType
    severity: Priority
    priority: Priority
    confidence: float = Field(ge=0, le=1)
    status: InformationStatus
    location: Location
    summary: str | None = None
    verified_facts: list[str] = Field(default_factory=list)
    uncertain_facts: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    report_count: int = Field(ge=0)
    created_at: datetime
    updated_at: datetime
    last_report_at: datetime


class IncidentUpdate(BaseModel):
    status: InformationStatus | None = None
    priority: Priority | None = None
    summary: str | None = Field(default=None, min_length=3, max_length=5000)
    recommended_action: str | None = Field(default=None, min_length=3, max_length=2000)

    @field_validator("summary", "recommended_action")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value else value


class TimelineEventRead(BaseModel):
    event_id: str
    incident_id: str
    event_type: str
    timestamp: datetime
    description: str
    source: str
    payload: dict = Field(default_factory=dict)


class ActionRead(BaseModel):
    incident_id: str
    recommended_actions: list[str]
    priority: Priority
    status: InformationStatus
