from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.incident import Incident, IncidentEvent
from app.schemas.incident import ActionRead, IncidentRead, IncidentUpdate, TimelineEventRead
from app.services.report_service import _report_count, update_incident
from app.services.serializers import event_data, incident_data
from app.services.websocket_manager import manager

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _incident_or_404(db: Session, incident_id: str) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.get("", response_model=list[IncidentRead])
def list_incidents(status: str | None = None, priority: str | None = None, db: Session = Depends(get_db)):
    statement = select(Incident).order_by(Incident.updated_at.desc())
    if status:
        statement = statement.where(Incident.status == status.upper())
    if priority:
        statement = statement.where(Incident.priority == priority.upper())
    return [incident_data(incident, _report_count(db, incident.id)) for incident in db.scalars(statement).all()]


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = _incident_or_404(db, incident_id)
    return incident_data(incident, _report_count(db, incident.id))


@router.get("/{incident_id}/timeline", response_model=list[TimelineEventRead])
def incident_timeline(incident_id: str, db: Session = Depends(get_db)):
    _incident_or_404(db, incident_id)
    events = db.scalars(select(IncidentEvent).where(IncidentEvent.incident_id == incident_id).order_by(IncidentEvent.timestamp.asc())).all()
    return [event_data(event) for event in events]


@router.get("/{incident_id}/actions", response_model=ActionRead)
def incident_actions(incident_id: str, db: Session = Depends(get_db)):
    incident = _incident_or_404(db, incident_id)
    return {"incident_id": incident.id, "recommended_actions": incident.recommended_action.split("\n") if incident.recommended_action else [], "priority": incident.priority, "status": incident.status}


@router.patch("/{incident_id}", response_model=IncidentRead)
async def patch_incident(incident_id: str, payload: IncidentUpdate, db: Session = Depends(get_db)):
    incident = _incident_or_404(db, incident_id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="At least one change is required")
    incident = update_incident(db, incident, changes)
    result = incident_data(incident, _report_count(db, incident.id))
    await manager.broadcast_incident(result)
    return result
