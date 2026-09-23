from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

def utcnow() -> datetime: return datetime.now(timezone.utc)

@dataclass
class ReportObservation:
    id: str; report_id: str; raw: dict[str, Any]; description: str
    incident_type: Optional[str] = None; location_name: Optional[str] = None
    latitude: Optional[float] = None; longitude: Optional[float] = None
    event_time: Optional[datetime] = None; received_at: datetime = field(default_factory=utcnow)
    source_type: str = 'anonymous_bystander'; people_affected: Optional[int] = None
    evidence: list[str] = field(default_factory=list); severity_indicators: list[str] = field(default_factory=list)
    entities: dict[str, Any] = field(default_factory=dict); claims: list[dict[str,str]] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list); extracted_summary: str = ''; extraction_confidence: float = 0.0

@dataclass
class MatchResult:
    left_report_id: str; right_report_id: str; score: float; classification: str
    location_score: float; time_score: float; semantic_score: float; type_score: float; reasons: list[str]

@dataclass
class IncidentClaim:
    claim_type: str; claim_value: str; source_report_id: str; confidence: float; freshness: str; created_at: datetime; status: str = 'supported'

@dataclass
class Contradiction:
    type: str; status: str; claims: list[dict[str, Any]]; requires_verification: bool = True

@dataclass
class IncidentEvidence:
    report_id: str; evidence_type: str; description: str; weight: float; created_at: datetime

@dataclass
class FusedIncident:
    incident_id: str; incident_type: Optional[str]; location: dict[str, Any]; report_ids: list[str]
    severity: str; priority: str; confidence: float; confidence_state: str; status: str; freshness: str
    verified_facts: list[dict[str,Any]]; uncertain_facts: list[dict[str,Any]]; contradictions: list[Contradiction]
    recommended_actions: list[str]; source_summary: dict[str,Any]; evidence: list[IncidentEvidence]
    timeline: list[dict[str,Any]]; explanation: dict[str,Any]; last_updated: datetime
    def to_dict(self):
        value=asdict(self); value['type']=value.pop('incident_type'); value['report_count']=len(self.report_ids); return _serialize(value)

def _serialize(value):
    if isinstance(value, datetime): return value.isoformat()
    if isinstance(value, dict): return {k:_serialize(v) for k,v in value.items()}
    if isinstance(value, list): return [_serialize(v) for v in value]
    return value
