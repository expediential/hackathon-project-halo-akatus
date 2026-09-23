from sqlalchemy import inspect
import asyncio
from app.db.database import engine
from tests.conftest import report_payload
from app.services.websocket_manager import ConnectionManager


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_database_initialization():
    assert {"reports", "incidents", "incident_events", "alerts"}.issubset(inspect(engine).get_table_names())


def test_create_and_retrieve_report(client):
    created = client.post("/api/reports", json=report_payload())
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["report"]["incident_type"] == "FIRE"
    assert body["incident"]["report_count"] == 1
    report_id = body["report"]["report_id"]
    assert client.get(f"/api/reports/{report_id}").json()["description"].startswith("Large fire")
    assert len(client.get("/api/reports").json()) == 1


def test_invalid_report_has_useful_validation_error(client):
    response = client.post("/api/reports", json=report_payload(latitude=101))
    assert response.status_code == 422
    assert "latitude" in response.text


def test_grouping_conflict_and_incident_views(client):
    first = client.post("/api/reports", json=report_payload(description="Fire is active at Block A"))
    incident_id = first.json()["incident"]["incident_id"]
    second = client.post("/api/reports", json=report_payload(source_type="AUTHORITY", description="Fire has been extinguished at Block A"))
    assert second.status_code == 201
    assert second.json()["conflict_detected"] is True
    incident = client.get(f"/api/incidents/{incident_id}")
    assert incident.status_code == 200
    assert incident.json()["status"] == "CONFLICTING"
    assert incident.json()["report_count"] == 2
    assert len(client.get(f"/api/incidents/{incident_id}/timeline").json()) >= 3
    assert client.get(f"/api/incidents/{incident_id}/actions").json()["recommended_actions"]


def test_update_incident(client):
    incident_id = client.post("/api/reports", json=report_payload()).json()["incident"]["incident_id"]
    response = client.patch(f"/api/incidents/{incident_id}", json={"status": "VERIFIED", "summary": "Verified by response team."})
    assert response.status_code == 200
    assert response.json()["status"] == "VERIFIED"
    assert response.json()["summary"] == "Verified by response team."


def test_websocket_manager_broadcasts_expected_event():
    class FakeSocket:
        def __init__(self):
            self.accepted = False
            self.messages = []

        async def accept(self):
            self.accepted = True

        async def send_json(self, payload):
            self.messages.append(payload)

    async def exercise():
        manager = ConnectionManager()
        socket = FakeSocket()
        await manager.connect(socket)
        await manager.broadcast_incident({"incident_id": "INC-TEST"})
        return socket

    socket = asyncio.run(exercise())
    assert socket.accepted is True
    assert socket.messages == [{"event": "incident.updated", "incident": {"incident_id": "INC-TEST"}}]
