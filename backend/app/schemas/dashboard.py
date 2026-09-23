from pydantic import BaseModel


class StatsRead(BaseModel):
    total_reports: int
    total_incidents: int
    active_incidents: int
    critical_incidents: int
    unacknowledged_alerts: int
