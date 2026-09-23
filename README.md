# Intelligence / Data Fusion Engine

This dependency-free Python package turns raw emergency observations into a traceable incident picture. It is deliberately deterministic for safety-critical decisions: no LLM is required, and an unavailable AI service cannot stop the pipeline.

## Backend boundary

```python
from intelligence import IntelligenceEngine

engine = IntelligenceEngine()
result = engine.process_report({
    "id": "R-42",
    "description": "Smoke and flames at Block A",
    "timestamp": "2026-09-23T10:42:00+00:00",
    "source_type": "identified_eyewitness",
})
# JSON-ready result: incident_id, type, severity, priority, confidence,
# evidence, claims, contradictions, timeline, explanation, actions.
```

Create one engine per persistence scope (for example, a backend service singleton). Persist the raw input and the returned record in the backend. The engine itself is in-memory and makes no database or web calls.

`engine.get_raw_report(report_id)` returns a copied original input for audit views. No raw report is overwritten or deleted during normalization/fusion.

## Pipeline and explainability

`normalize_report` preserves the raw mapping and extracts only explicit or rule-detected values. Missing values remain `None`. It normalizes case, whitespace, `Blk`/`Block`, source aliases, coordinates, and ISO timestamps. It also extracts a small set of incident, location, count, and status claims using transparent patterns.

Each pair of plausible reports is scored as:

`0.30 × semantic + 0.30 × location + 0.20 × time + 0.20 × type`

Location uses either Haversine distance (default radius: 500m) or normalized location text. Time decreases linearly over the default 60-minute window. Text uses token overlap plus character-sequence similarity. Scores at least `0.90` are **duplicate**; scores at least `0.65` with the same known incident type are **related**; possible matches are never silently merged. Detailed component scores and reasons appear under `explanation.matching`.

Clusters retain every source report ID and generate `DIRECT_OBSERVATION`, location, matching, stale-information, and conflicting-claim evidence. The same production pipeline powers `demo_reports()`.

## Confidence and freshness

Source reliability is a configurable prior, separate from incident confidence:

| source | prior |
| --- | ---: |
| authority | .95 |
| verified responder | .90 |
| security / sensor | .85 |
| identified eyewitness | .65 |
| anonymous bystander | .50 |
| social media | .35 |

Confidence blends source prior (35%), report/source corroboration (30%), freshness (20%), and supplied evidence (15%), then deducts 0.15 per contradictory claim-set up to 0.35. Freshness is `fresh <15m`, `recent <30m`, `stale <60m`, otherwise `outdated`. These are prototype settings, not official operational standards.

**Confidence measures the strength of available evidence, not truth.** High confidence never marks an assertion as independently verified. Contradictory claims stay visible in `uncertain_facts`, `contradictions`, evidence, and the timeline.

## Deterministic safety decisions

Severity rules are in `priority`: active/large fire, trapped people, mass casualty, collapse, or immediate life threat is critical; serious injuries, gas leak, blocked evacuation, and escalation are high; known medical, flooding, security, or accident incidents default to medium; remaining reports are low. Priority uses severity, immediate phrasing, explicitly stated affected-person count, confidence, and known geographic relevance to deterministically produce P0–P3.

Actions are intentionally conservative rules in `actions`. They do not invent specialist procedures or claim to contact anyone. Any detected contradiction appends an updated-confirmation recommendation.

## Suggested FastAPI adapter

Keep routes in the existing backend, calling the engine rather than importing its internals. The returned dict already supplies the data for analyze/fuse, incident detail, evidence, claims, conflicts, timeline, and explanation endpoints. Persisting it enables retrieval routes without coupling the backend to this package’s implementation.

## Limits

The fallback extractor handles a useful, deliberately small English vocabulary. It does not provide geocoding, named-entity recognition, cross-language understanding, persistence, or real-world verification. An optional AI extractor can be added before deterministic validation, but it must never replace severity, priority, conflict preservation, or action rules.
