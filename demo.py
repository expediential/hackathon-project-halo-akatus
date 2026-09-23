"""Synthetic demo data that travels through the production fusion pipeline."""

from datetime import datetime, timezone


def demo_reports() -> list[dict]:
    base = "2026-09-23T10:"
    return [
        {"id": "R001", "description": "Large fire reported near Block A.", "timestamp": base + "30:00+00:00", "source_type": "identified_eyewitness"},
        {"id": "R002", "description": "Smoke and flames visible around Block A.", "timestamp": base + "34:00+00:00", "source_type": "social_media"},
        {"id": "R003", "description": "Fire reported at Block A at 10:42.", "timestamp": base + "42:00+00:00", "source_type": "security"},
        {"id": "R004", "description": "Emergency vehicle moving toward Block A.", "incident_type": "fire", "location": "Block A", "timestamp": base + "43:00+00:00", "source_type": "verified_responder"},
        {"id": "R005", "description": "Fire appears to be under control at Block A.", "timestamp": base + "47:00+00:00", "source_type": "identified_eyewitness"},
        {"id": "R006", "description": "Fire has been extinguished at Block A.", "timestamp": base + "50:00+00:00", "source_type": "authority"},
        {"id": "R007", "description": "Road accident near Gate 2.", "timestamp": base + "31:00+00:00", "source_type": "anonymous_bystander"},
        {"id": "R008", "description": "Traffic blocked because of accident near Gate 2.", "timestamp": base + "36:00+00:00", "source_type": "security"},
        {"id": "R009", "description": "Minor accident reported at Gate 2.", "timestamp": base + "39:00+00:00", "source_type": "social_media"},
        {"id": "R010", "description": "Road is now clear at Gate 2.", "incident_type": "accident", "location": "Gate 2", "timestamp": base + "55:00+00:00", "source_type": "authority"},
    ]
