# ATOM HALO Emergency API

FastAPI backend for PS-009, **The First Five Minutes**. It accepts reports from multiple channels, groups related reports into incidents, preserves the original evidence, flags potential conflicts/staleness, creates transparent prototype priority recommendations, and emits live incident updates.

## Run locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the generated API contract. Copy `.env.example` to `.env` to configure the database, match threshold, CORS origins, and freshness threshold. SQLite is the local default; set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL for deployment.

## API

| Endpoint | Purpose |
| --- | --- |
| `POST /api/reports` | Validate, normalize, process, store, group, and return a report/incident. |
| `GET /api/reports`, `GET /api/reports/{report_id}` | Read original stored reports. |
| `GET /api/incidents`, `GET /api/incidents/{incident_id}` | Read incident dashboard data. |
| `GET /api/incidents/{id}/timeline` | Read append-only audit/timeline events. |
| `GET /api/incidents/{id}/actions` | Read recommendations. |
| `PATCH /api/incidents/{id}` | Update status, priority, summary, or action with an audit event. |
| `GET /api/alerts`, `GET /api/stats`, `GET /api/health` | Dashboard support and service health. |
| `WS /ws/incidents` | Sends `{ "event": "incident.updated", "incident": { ... } }`. |

## Processing rules and assumptions

The initial `MockIntelligenceAdapter` is a replaceable service boundary for the intelligence team's extraction/classification adapter. It uses deterministic keyword extraction and never fabricates missing location or facts. No database model is coupled to that adapter's internals.

Grouping is a **possible-match** decision: 35% incident type, 30% location, 20% description token overlap, and 15% time proximity (within six hours). The default grouping threshold is `0.62`; both it and freshness are environment-configurable. A matching report attaches to the existing incident rather than creating a new one.

Reports older than `OUTDATED_THRESHOLD_MINUTES` are labelled `OUTDATED`, not false. Opposing active/resolved phrases produce `CONFLICTING`, never an automatic resolution. `VERIFIED` is only assigned under this illustrative prototype rule: at least two grouped reports including an `AUTHORITY` or `EMERGENCY_SERVICE` report. Source labels are configurable display context, not real-world reliability claims.

Priority is an intentionally transparent hackathon scoring heuristic based on incident type, severity indicators, corroboration, conflicts, and freshness; it is not an official emergency-response model. Recommendations are decision-support prompts and must be reviewed by trained responders.

## Tests

```powershell
cd backend
pytest -q
```

Tests cover database initialization, health, validation, report ingestion/retrieval, incident grouping/conflicts/timelines/actions, updates, and WebSocket broadcasts.
