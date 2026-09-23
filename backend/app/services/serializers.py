from app.models.incident import Incident, IncidentEvent
from app.models.report import EmergencyReport
from app.models.alert import Alert


def incident_data(incident: Incident, report_count: int) -> dict:
    actions = incident.recommended_action.split("\n") if incident.recommended_action else []
    return {"incident_id": incident.id, "type": incident.incident_type, "severity": incident.priority, "priority": incident.priority, "confidence": incident.confidence, "status": incident.status, "location": {"latitude": incident.latitude, "longitude": incident.longitude, "location_name": incident.location_name}, "summary": incident.summary, "verified_facts": incident.verified_facts or [], "uncertain_facts": incident.uncertain_facts or [], "contradictions": incident.contradictions or [], "recommended_actions": actions, "report_count": report_count, "created_at": incident.created_at, "updated_at": incident.updated_at, "last_report_at": incident.last_report_at}


def report_data(report: EmergencyReport) -> dict:
    duplicate = None
    if report.duplicate_similarity is not None:
        duplicate = {"is_possible_duplicate": report.duplicate_similarity > 0, "similarity": report.duplicate_similarity, "reason": "Similarity assessed during ingestion"}
    return {"report_id": report.id, "source_type": report.source_type, "description": report.description, "incident_type": report.incident_type, "location": {"latitude": report.latitude, "longitude": report.longitude, "location_name": report.location_name}, "reported_at": report.reported_at, "received_at": report.received_at, "status": report.status, "priority": report.priority, "incident_id": report.incident_id, "is_outdated": report.is_outdated, "evidence": report.evidence or [], "metadata": report.metadata_ or {}, "extraction": report.extraction or {}, "duplicate": duplicate, "created_at": report.created_at}


def event_data(event: IncidentEvent) -> dict:
    return {"event_id": event.id, "incident_id": event.incident_id, "event_type": event.event_type, "timestamp": event.timestamp, "description": event.description, "source": event.source, "payload": event.payload or {}}


def alert_data(alert: Alert) -> dict:
    return {"id": alert.id, "incident_id": alert.incident_id, "alert_type": alert.alert_type, "severity": alert.severity, "title": alert.title, "message": alert.message, "is_read": alert.is_read, "created_at": alert.created_at}
