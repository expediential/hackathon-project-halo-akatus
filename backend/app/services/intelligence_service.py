"""Replaceable integration boundary for Engineer 3's intelligence layer.

The deterministic adapter keeps the API usable without an external model. A future
adapter only needs to implement ``process_report(report) -> IntelligenceResult``.
"""
from dataclasses import dataclass
from app.models.enums import IncidentType


@dataclass(frozen=True)
class IntelligenceResult:
    incident_type: IncidentType
    inferred_location: str | None
    severity_indicators: list[str]
    summary: str


class MockIntelligenceAdapter:
    _keywords = {
        IncidentType.FIRE: ("fire", "flame", "smoke", "burning"),
        IncidentType.ACCIDENT: ("accident", "collision", "crash", "vehicle"),
        IncidentType.MEDICAL: ("medical", "injured", "unconscious", "ambulance"),
        IncidentType.NATURAL_DISASTER: ("flood", "earthquake", "landslide", "storm"),
        IncidentType.PUBLIC_SAFETY: ("violence", "attack", "crowd", "threat"),
        IncidentType.INFRASTRUCTURE: ("collapse", "gas leak", "power line", "building damage"),
    }
    _severity_phrases = ("large", "major", "critical", "trapped", "multiple", "smoke visible", "injured", "unconscious")

    def process_report(self, report) -> IntelligenceResult:
        text = report.description.lower()
        incident_type = next((kind for kind, words in self._keywords.items() if any(word in text for word in words)), IncidentType.UNKNOWN)
        indicators = [phrase for phrase in self._severity_phrases if phrase in text]
        return IntelligenceResult(
            incident_type=incident_type,
            inferred_location=report.location_name,
            severity_indicators=indicators,
            summary=report.description[:280],
        )


intelligence_adapter = MockIntelligenceAdapter()
