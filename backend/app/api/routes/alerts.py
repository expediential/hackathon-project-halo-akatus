from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertRead
from app.services.serializers import alert_data

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertRead])
def list_alerts(unread_only: bool = False, db: Session = Depends(get_db)):
    statement = select(Alert).order_by(Alert.created_at.desc())
    if unread_only:
        statement = statement.where(Alert.is_read.is_(False))
    return [alert_data(alert) for alert in db.scalars(statement).all()]
