from app.models.enums import IncidentType, InformationStatus, Priority


BASE_ACTIONS = {
    IncidentType.FIRE: "Dispatch fire response and establish a safe perimeter.",
    IncidentType.MEDICAL: "Dispatch medical responders and assess immediate patient needs.",
    IncidentType.ACCIDENT: "Dispatch responders and manage the immediate scene hazard.",
    IncidentType.NATURAL_DISASTER: "Notify emergency coordination and assess affected area.",
    IncidentType.PUBLIC_SAFETY: "Notify public-safety responders and preserve scene safety.",
    IncidentType.INFRASTRUCTURE: "Isolate the infrastructure hazard and notify relevant responders.",
}


def recommended_actions(incident_type: IncidentType, priority: Priority, status: InformationStatus) -> list[str]:
    actions = [BASE_ACTIONS.get(incident_type, "Request on-scene verification and classify the incident.")]
    if priority in {Priority.CRITICAL, Priority.HIGH}:
        actions.append("Escalate to the incident commander for immediate review.")
    if status == InformationStatus.CONFLICTING:
        actions.append("Request independent verification before resolving conflicting reports.")
    elif status == InformationStatus.OUTDATED:
        actions.append("Request a current status update before acting on stale information.")
    return actions
