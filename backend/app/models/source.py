"""Illustrative source display metadata, deliberately not a reliability ranking."""
from app.models.enums import SourceType

SOURCE_METADATA = {
    SourceType.CITIZEN: {"label": "Citizen", "context": "Publicly submitted report"},
    SourceType.EMERGENCY_SERVICE: {"label": "Emergency Service", "context": "Responder-system report"},
    SourceType.SOCIAL_MEDIA: {"label": "Social Media", "context": "Public online report"},
    SourceType.CCTV_SYSTEM: {"label": "CCTV/System", "context": "System-generated observation"},
    SourceType.AUTHORITY: {"label": "Authority", "context": "Authority-system report"},
    SourceType.OTHER: {"label": "Other", "context": "Unclassified source"},
}
