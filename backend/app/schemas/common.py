from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Location(BaseModel):
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    location_name: str | None = Field(default=None, max_length=255)

    @field_validator("location_name")
    @classmethod
    def normalize_location(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value else None


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
