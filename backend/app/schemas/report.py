from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator, model_validator
from app.models.enums import IncidentType, InformationStatus, Priority, SourceType
from app.schemas.common import Location


class ReportCreate(Location):
    source_type: SourceType
    description: str = Field(min_length=3, max_length=5000)
    reported_at: datetime
    evidence: list[str] = Field(default_factory=list, max_length=20)
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("reported_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def location_is_not_half_specified(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")
        return self


class DuplicateAssessment(BaseModel):
    is_possible_duplicate: bool
    similarity: float = Field(ge=0, le=1)
    reason: str


class ReportRead(BaseModel):
    report_id: str
    source_type: SourceType
    description: str
    incident_type: IncidentType
    location: Location
    reported_at: datetime
    received_at: datetime
    status: InformationStatus
    priority: Priority
    incident_id: str
    is_outdated: bool
    evidence: list[str]
    metadata: dict
    extraction: dict
    duplicate: DuplicateAssessment | None = None
    created_at: datetime


class ReportProcessResponse(BaseModel):
    report: ReportRead
    incident: "IncidentRead"
    duplicate: DuplicateAssessment
    conflict_detected: bool
    conflict_description: str | None = None
    requires_verification: bool


from app.schemas.incident import IncidentRead  # noqa: E402
ReportProcessResponse.model_rebuild()
