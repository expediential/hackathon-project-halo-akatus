from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.report import EmergencyReport
from app.schemas.dashboard import StatsRead

router = APIRouter(tags=["dashboard"])


@router.get("/stats", response_model=StatsRead)
def stats(db: Session = Depends(get_db)):
    count = lambda model, *filters: db.scalar(select(func.count()).select_from(model).where(*filters)) or 0
    return {"total_reports": count(EmergencyReport), "total_incidents": count(Incident), "active_incidents": count(Incident, Incident.status.in_(["UNVERIFIED", "VERIFIED", "CONFLICTING"])), "critical_incidents": count(Incident, Incident.priority == "CRITICAL"), "unacknowledged_alerts": count(Alert, Alert.is_read.is_(False))}
