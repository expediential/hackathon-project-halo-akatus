from app.models.enums import IncidentType, InformationStatus, Priority


def calculate_priority(incident_type: IncidentType, severity_indicators: list[str], report_count: int, status: InformationStatus, is_outdated: bool) -> tuple[Priority, int]:
    """Transparent illustrative scoring, not an operational emergency model."""
    score = {IncidentType.FIRE: 40, IncidentType.MEDICAL: 40, IncidentType.NATURAL_DISASTER: 35, IncidentType.PUBLIC_SAFETY: 35, IncidentType.ACCIDENT: 30, IncidentType.INFRASTRUCTURE: 30}.get(incident_type, 15)
    score += min(20, len(severity_indicators) * 7)
    score += min(15, max(0, report_count - 1) * 5)
    if status.value == "CONFLICTING": score += 8
    if is_outdated: score -= 10
    priority = Priority.CRITICAL if score >= 60 else Priority.HIGH if score >= 40 else Priority.MEDIUM if score >= 25 else Priority.LOW
    return priority, max(score, 0)
