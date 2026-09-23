from datetime import datetime
from pydantic import BaseModel
from app.models.enums import AlertType, Priority


class AlertRead(BaseModel):
    id: str
    incident_id: str
    alert_type: AlertType
    severity: Priority
    title: str
    message: str
    is_read: bool
    created_at: datetime
