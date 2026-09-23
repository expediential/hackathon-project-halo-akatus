from dataclasses import dataclass
from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
import re
from app.models.incident import Incident
from app.services.intelligence_service import IntelligenceResult

STOP_WORDS = {"a", "an", "the", "at", "near", "reported", "report", "is", "was", "and", "of", "to", "in", "on", "from", "large"}


@dataclass(frozen=True)
class MatchResult:
    incident: Incident | None
    similarity: float
    reason: str


def _tokens(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOP_WORDS}


def _text_similarity(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    return len(a & b) / len(a | b) if a and b else 0.0


def _distance_km(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    d_lat, d_lon = radians(lat_b - lat_a), radians(lon_b - lon_a)
    value = sin(d_lat / 2) ** 2 + cos(radians(lat_a)) * cos(radians(lat_b)) * sin(d_lon / 2) ** 2
    return 6371 * 2 * asin(sqrt(value))


def score_incident(report, extraction: IntelligenceResult, incident: Incident) -> tuple[float, str]:
    type_score = 1.0 if incident.incident_type == extraction.incident_type.value else 0.0
    description_score = _text_similarity(report.description, incident.summary or "")
    location_score = 0.0
    if report.latitude is not None and incident.latitude is not None:
        location_score = max(0.0, 1 - _distance_km(report.latitude, report.longitude, incident.latitude, incident.longitude) / 2)
    elif report.location_name and incident.location_name:
        location_score = 1.0 if report.location_name.lower() == incident.location_name.lower() else _text_similarity(report.location_name, incident.location_name)
    last_report_at = incident.last_report_at.replace(tzinfo=timezone.utc) if incident.last_report_at.tzinfo is None else incident.last_report_at.astimezone(timezone.utc)
    reported_at = report.reported_at.replace(tzinfo=timezone.utc) if report.reported_at.tzinfo is None else report.reported_at.astimezone(timezone.utc)
    hours = abs((reported_at - last_report_at).total_seconds()) / 3600
    time_score = max(0.0, 1 - hours / 6)
    score = round(0.35 * type_score + 0.30 * location_score + 0.20 * description_score + 0.15 * time_score, 2)
    signals = []
    if type_score: signals.append("same incident type")
    if location_score >= 0.5: signals.append("nearby or matching location")
    if time_score >= 0.5: signals.append("close report time")
    if description_score >= 0.25: signals.append("similar description")
    return score, ", ".join(signals) or "limited shared signals"


def find_best_match(report, extraction: IntelligenceResult, incidents: list[Incident]) -> MatchResult:
    candidates = [(*score_incident(report, extraction, incident), incident) for incident in incidents]
    if not candidates:
        return MatchResult(None, 0.0, "No existing incident candidates")
    score, reason, incident = max(candidates, key=lambda candidate: candidate[0])
    return MatchResult(incident, score, reason)
