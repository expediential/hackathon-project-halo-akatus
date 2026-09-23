from dataclasses import dataclass


@dataclass(frozen=True)
class ConflictResult:
    detected: bool
    description: str | None = None


ACTIVE_TERMS = {"active", "spreading", "ongoing", "burning", "uncontrolled"}
RESOLVED_TERMS = {"extinguished", "resolved", "contained", "cleared", "safe"}


def _state(text: str) -> str | None:
    tokens = set(text.lower().replace(".", " ").split())
    if tokens & ACTIVE_TERMS:
        return "active"
    if tokens & RESOLVED_TERMS:
        return "resolved"
    return None


def detect_conflict(description: str, prior_descriptions: list[str]) -> ConflictResult:
    incoming_state = _state(description)
    if not incoming_state:
        return ConflictResult(False)
    for previous in prior_descriptions:
        existing_state = _state(previous)
        if existing_state and existing_state != incoming_state:
            return ConflictResult(True, "Sources provide different incident-status information; verification is required.")
    return ConflictResult(False)
