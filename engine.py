"""Stable callable boundary for the intelligence/data-fusion subsystem."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from itertools import count
from typing import Any, Iterable

from intelligence.actions import recommend_actions
from intelligence.confidence import assess_confidence, freshness
from intelligence.contradiction import claims_from_reports, find_contradictions
from intelligence.deduplication import cluster_reports
from intelligence.models import FusedIncident, IncidentEvidence, ReportObservation
from intelligence.normalization import normalize_report
from intelligence.priority import determine_priority, determine_severity


class IntelligenceEngine:
    """In-memory fusion engine suitable for a backend service adapter.

    The backend owns persistence: after calling this class it can persist raw
    reports and ``result.to_dict()``.  This keeps the intelligence boundary
    small, deterministic, testable, and independent of FastAPI or a database.
    """

    def __init__(self, *, location_radius_meters: int = 500, time_window_minutes: int = 60,
                 source_reliability: dict[str, float] | None = None) -> None:
        self.location_radius_meters = location_radius_meters
        self.time_window_minutes = time_window_minutes
        self.source_reliability = source_reliability
        self._reports: list[ReportObservation] = []
        self._incidents: dict[str, FusedIncident] = {}
        self._sequence = count(1)

    def process_report(self, report: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
        """Normalize one raw report, fuse it, and return its incident picture.

        This method does not make network calls, use an LLM, or mutate the raw
        mapping supplied by the caller. Unknown fields stay ``None``.
        """
        observation = normalize_report(report)
        self._reports.append(observation)
        self._rebuild(now=now)
        return self.get_incident_for_report(observation.report_id)

    def process_reports(self, reports: Iterable[dict[str, Any]], *, now: datetime | None = None) -> list[dict[str, Any]]:
        """Fuse a batch. The same pipeline is used for demos and live reports."""
        observations = [normalize_report(report) for report in reports]
        self._reports.extend(observations)
        self._rebuild(now=now)
        return [self.get_incident_for_report(item.report_id) for item in observations]

    def get_incident(self, incident_id: str) -> dict[str, Any]:
        return self._incidents[incident_id].to_dict()

    def get_incident_for_report(self, report_id: str) -> dict[str, Any]:
        for incident in self._incidents.values():
            if report_id in incident.report_ids:
                return incident.to_dict()
        raise KeyError(f"No fused incident contains report {report_id!r}")

    def list_incidents(self) -> list[dict[str, Any]]:
        return [incident.to_dict() for incident in self._incidents.values()]

    def get_raw_report(self, report_id: str) -> dict[str, Any]:
        """Return an untouched copy of the source report for audit display."""
        for report in self._reports:
            if report.report_id == report_id:
                return dict(report.raw)
        raise KeyError(f"Unknown report {report_id!r}")

    def _rebuild(self, *, now: datetime | None) -> None:
        clusters, matches = cluster_reports(
            self._reports, radius_meters=self.location_radius_meters, time_window_minutes=self.time_window_minutes,
        )
        previous_ids = {frozenset(incident.report_ids): incident.incident_id for incident in self._incidents.values()}
        rebuilt: dict[str, FusedIncident] = {}
        for reports in clusters:
            report_ids = frozenset(report.report_id for report in reports)
            incident_id = previous_ids.get(report_ids, f"INC-{next(self._sequence):04d}")
            relevant_matches = [match for match in matches if match.left_report_id in report_ids and match.right_report_id in report_ids]
            rebuilt[incident_id] = self._fuse(incident_id, reports, relevant_matches, now=now)
        self._incidents = rebuilt

    def _fuse(self, incident_id: str, reports: list[ReportObservation], matches: list[Any], *, now: datetime | None) -> FusedIncident:
        now = now or datetime.now(timezone.utc)
        type_counter = Counter(report.incident_type for report in reports if report.incident_type)
        incident_type = type_counter.most_common(1)[0][0] if type_counter else None
        location_counter = Counter(report.location_name for report in reports if report.location_name)
        location_name = location_counter.most_common(1)[0][0] if location_counter else None
        coordinates = next(((report.latitude, report.longitude) for report in reports if report.latitude is not None and report.longitude is not None), (None, None))
        claims = claims_from_reports(reports)
        contradictions = find_contradictions(claims)
        confidence, confidence_state, confidence_reasons = assess_confidence(reports, contradictions, now=now, source_reliability=self.source_reliability)
        severity = determine_severity(reports)
        geographic_relevance = 1.0 if location_name or coordinates[0] is not None else .45
        priority = determine_priority(severity, reports, confidence, geographic_relevance)
        latest = max((report.event_time or report.received_at for report in reports), default=now)
        freshness_state, _ = freshness(latest, now)
        status = "conflicting" if contradictions else "active"
        evidence: list[IncidentEvidence] = []
        for report in reports:
            report_time = report.event_time or report.received_at
            evidence.append(IncidentEvidence(report.report_id, "DIRECT_OBSERVATION", "Raw report retained as contributing evidence.", .5, report_time))
            if report.location_name:
                evidence.append(IncidentEvidence(report.report_id, "LOCATION_MATCH", f"Normalized location: {report.location_name}", .7, report_time))
            if freshness(report_time, now)[0] in {"stale", "outdated"}:
                evidence.append(IncidentEvidence(report.report_id, "OUTDATED_REPORT", "Older information remains in history with lower current relevance.", .3, report_time))
        for match in matches:
            evidence.append(IncidentEvidence(match.left_report_id, "FUSION_MATCH", "; ".join(match.reasons), match.score, latest))
        for conflict in contradictions:
            for claim in conflict.claims:
                evidence.append(IncidentEvidence(claim["report_id"], "CONFLICTING_CLAIM", f"{conflict.type}: {claim['value']}", .0, latest))
        source_counts = Counter(report.source_type for report in reports)
        # Report-derived claims are never promoted to verified facts by this
        # module. Verification is an external operational decision; even a
        # highly reliable source is evidence, not guaranteed truth.
        verified_facts = []
        uncertain_facts = []
        for claim in claims:
            item = {"type": claim.claim_type, "value": claim.claim_value, "report_id": claim.source_report_id, "freshness": claim.freshness}
            uncertain_facts.append(item)
        timeline = [{"time": (report.event_time or report.received_at), "report_id": report.report_id, "description": report.description, "freshness": freshness(report.event_time or report.received_at, now)[0]} for report in reports]
        timeline.sort(key=lambda item: item["time"])
        match_reasons = [reason for match in matches for reason in match.reasons]
        explanation = {
            "decision": "CLUSTERED" if len(reports) > 1 else "SINGLE_REPORT",
            "matching": [{"reports": [match.left_report_id, match.right_report_id], "classification": match.classification, "score": match.score, "reasons": match.reasons} for match in matches],
            "confidence_factors": confidence_reasons,
            "limits": "Confidence measures the strength of available evidence; it does not verify truth.",
            "fusion_reasons": list(dict.fromkeys(match_reasons)),
        }
        return FusedIncident(
            incident_id=incident_id, incident_type=incident_type,
            location={"name": location_name, "latitude": coordinates[0], "longitude": coordinates[1]},
            report_ids=[report.report_id for report in reports], severity=severity, priority=priority,
            confidence=confidence, confidence_state=confidence_state, status=status, freshness=freshness_state,
            verified_facts=verified_facts, uncertain_facts=uncertain_facts, contradictions=contradictions,
            recommended_actions=recommend_actions(incident_type, contradictions),
            source_summary={"source_counts": dict(source_counts), "source_count": len(source_counts), "independent_source_count": len(source_counts)},
            evidence=evidence, timeline=timeline, explanation=explanation, last_updated=latest,
        )


_default_engine = IntelligenceEngine()


def process_report(report: dict[str, Any]) -> dict[str, Any]:
    """Convenience interface for small integrations; use an instance for isolation."""
    return _default_engine.process_report(report)
