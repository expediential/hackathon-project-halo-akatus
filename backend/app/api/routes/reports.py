from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.report import EmergencyReport
from app.schemas.report import ReportCreate, ReportProcessResponse, ReportRead
from app.services.report_service import process_report, _report_count
from app.services.serializers import incident_data, report_data
from app.services.websocket_manager import manager

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportProcessResponse, status_code=status.HTTP_201_CREATED)
async def create_report(payload: ReportCreate, db: Session = Depends(get_db)):
    report, incident, duplicate, conflict, conflict_description = process_report(db, payload)
    incident_response = incident_data(incident, _report_count(db, incident.id))
    await manager.broadcast_incident(incident_response)
    return {"report": report_data(report), "incident": incident_response, "duplicate": duplicate, "conflict_detected": conflict, "conflict_description": conflict_description, "requires_verification": conflict or incident.status != "VERIFIED"}


@router.get("", response_model=list[ReportRead])
def list_reports(incident_id: str | None = None, db: Session = Depends(get_db)):
    statement = select(EmergencyReport).order_by(EmergencyReport.received_at.desc())
    if incident_id:
        statement = statement.where(EmergencyReport.incident_id == incident_id)
    return [report_data(report) for report in db.scalars(statement).all()]


@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.get(EmergencyReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report_data(report)
