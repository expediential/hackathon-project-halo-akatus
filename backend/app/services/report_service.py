from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.alert import Alert
from app.models.enums import AlertType, InformationStatus, Priority, SourceType
from app.models.incident import Incident, IncidentEvent
from app.models.report import EmergencyReport
from app.schemas.report import DuplicateAssessment, ReportCreate
from app.services.conflict_service import detect_conflict
from app.services.duplicate_service import find_best_match
from app.services.intelligence_service import intelligence_adapter
from app.services.priority_service import calculate_priority
from app.services.recommendation_service import recommended_actions


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def add_event(db: Session, incident_id: str, event_type: str, description: str, source: str = "SYSTEM", payload: dict | None = None) -> None:
    db.add(IncidentEvent(incident_id=incident_id, event_type=event_type, description=description, source=source, payload=payload or {}))


def _create_alerts(db: Session, incident: Incident, conflict: bool, outdated: bool) -> None:
    alerts: list[Alert] = []
    if conflict:
        alerts.append(Alert(incident_id=incident.id, alert_type=AlertType.CONFLICT_DETECTED.value, severity=Priority.HIGH.value, title="Conflicting incident information", message="Independent verification is required before resolving this incident."))
    if outdated:
        alerts.append(Alert(incident_id=incident.id, alert_type=AlertType.OUTDATED_INFORMATION.value, severity=Priority.MEDIUM.value, title="Potentially outdated report", message="A report exceeds the configured freshness threshold."))
    if incident.priority == Priority.CRITICAL.value:
        alerts.append(Alert(incident_id=incident.id, alert_type=AlertType.CRITICAL_INCIDENT.value, severity=Priority.CRITICAL.value, title="Critical incident", message="A critical incident requires immediate review."))
    elif incident.priority == Priority.HIGH.value:
        alerts.append(Alert(incident_id=incident.id, alert_type=AlertType.HIGH_PRIORITY.value, severity=Priority.HIGH.value, title="High-priority incident", message="A high-priority incident requires prompt review."))
    if _report_count(db, incident.id) >= 2:
        alerts.append(Alert(incident_id=incident.id, alert_type=AlertType.MULTIPLE_REPORTS.value, severity=incident.priority, title="Multiple reports grouped", message="Several reports have been grouped under this incident."))
    db.add_all(alerts)


def _report_count(db: Session, incident_id: str) -> int:
    return len(db.scalars(select(EmergencyReport).where(EmergencyReport.incident_id == incident_id)).all())


def _incident_reports(db: Session, incident_id: str) -> list[EmergencyReport]:
    return db.scalars(select(EmergencyReport).where(EmergencyReport.incident_id == incident_id).order_by(EmergencyReport.reported_at)).all()


def process_report(db: Session, payload: ReportCreate) -> tuple[EmergencyReport, Incident, DuplicateAssessment, bool, str | None]:
    extraction = intelligence_adapter.process_report(payload)
    incidents = db.scalars(select(Incident)).all()
    match = find_best_match(payload, extraction, incidents)
    threshold = get_settings().incident_match_threshold
    matched_incident = match.incident if match.incident and match.similarity >= threshold else None
    outdated = (datetime.now(timezone.utc) - as_utc(payload.reported_at)).total_seconds() > get_settings().outdated_threshold_minutes * 60

    if matched_incident is None:
        incident = Incident(
            incident_type=extraction.incident_type.value,
            location_name=payload.location_name or extraction.inferred_location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            summary=extraction.summary,
            last_report_at=payload.reported_at,
        )
        db.add(incident)
        db.flush()
        prior_reports: list[EmergencyReport] = []
        duplicate = DuplicateAssessment(is_possible_duplicate=False, similarity=match.similarity, reason="No incident exceeded the grouping threshold")
        add_event(db, incident.id, "incident.created", "Incident created from incoming report", payload={"similarity": match.similarity})
    else:
        incident = matched_incident
        prior_reports = _incident_reports(db, incident.id)
        duplicate = DuplicateAssessment(is_possible_duplicate=True, similarity=match.similarity, reason=match.reason)

    conflict = detect_conflict(payload.description, [report.description for report in prior_reports])
    authoritative = payload.source_type in {SourceType.AUTHORITY, SourceType.EMERGENCY_SERVICE}
    report_count = len(prior_reports) + 1
    status = InformationStatus.CONFLICTING if conflict.detected else InformationStatus.OUTDATED if outdated else InformationStatus.VERIFIED if authoritative and report_count >= 2 else InformationStatus.UNVERIFIED
    priority, _score = calculate_priority(extraction.incident_type, extraction.severity_indicators, report_count, status, outdated)
    actions = recommended_actions(extraction.incident_type, priority, status)

    report = EmergencyReport(
        source_type=payload.source_type.value,
        description=payload.description,
        incident_type=extraction.incident_type.value,
        location_name=payload.location_name or extraction.inferred_location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        reported_at=payload.reported_at,
        status=status.value,
        priority=priority.value,
        incident_id=incident.id,
        is_outdated=outdated,
        evidence=payload.evidence,
        metadata_=payload.metadata,
        extraction={"incident_type": extraction.incident_type.value, "location": extraction.inferred_location, "severity_indicators": extraction.severity_indicators},
        duplicate_similarity=duplicate.similarity,
    )
    db.add(report)
    db.flush()  # Materialize the report ID before writing its audit event.
    incident.incident_type = extraction.incident_type.value if incident.incident_type == "UNKNOWN" else incident.incident_type
    incident.status = status.value
    incident.priority = priority.value
    incident.last_report_at = max(as_utc(incident.last_report_at), as_utc(payload.reported_at))
    incident.summary = extraction.summary if report_count == 1 else f"{incident.incident_type}: {report_count} related reports at {incident.location_name or 'an unspecified location'}."
    incident.recommended_action = "\n".join(actions)
    incident.confidence = round(min(0.95, 0.35 + 0.15 * report_count + (0.15 if authoritative else 0) - (0.2 if conflict.detected else 0)), 2)
    incident.uncertain_facts = list(dict.fromkeys([*incident.uncertain_facts, "Information remains subject to field verification."]))
    if status == InformationStatus.VERIFIED:
        incident.verified_facts = list(dict.fromkeys([*incident.verified_facts, f"Corroborated by {report_count} reports including an authorized source."]))
    if conflict.description:
        incident.contradictions = list(dict.fromkeys([*incident.contradictions, conflict.description]))
    add_event(db, incident.id, "report.received", f"Report {report.id} received from {payload.source_type.value}", source=payload.source_type.value, payload={"report_id": report.id, "possible_duplicate": duplicate.is_possible_duplicate, "similarity": duplicate.similarity})
    if conflict.detected:
        add_event(db, incident.id, "conflict.detected", conflict.description or "Conflict detected")
    if outdated:
        add_event(db, incident.id, "report.outdated", f"Report {report.id} is older than the configured freshness threshold")
    _create_alerts(db, incident, conflict.detected, outdated)
    db.commit()
    db.refresh(report)
    db.refresh(incident)
    return report, incident, duplicate, conflict.detected, conflict.description


def update_incident(db: Session, incident: Incident, changes: dict) -> Incident:
    before = {key: getattr(incident, key) for key in changes}
    for key, value in changes.items():
        if key == "recommended_action":
            setattr(incident, key, value)
        else:
            setattr(incident, key, value.value if hasattr(value, "value") else value)
    add_event(db, incident.id, "incident.updated", "Incident updated by API", source="API", payload={"before": before, "after": {key: str(value.value if hasattr(value, 'value') else value) for key, value in changes.items()}})
    db.commit()
    db.refresh(incident)
    return incident
