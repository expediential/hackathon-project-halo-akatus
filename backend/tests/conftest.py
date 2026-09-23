import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["DATABASE_URL"] = f"sqlite:///{(ROOT / 'test_halo.db').as_posix()}"
os.environ["OUTDATED_THRESHOLD_MINUTES"] = "60"

from app.db.database import Base, engine, init_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def report_payload(**overrides):
    payload = {"source_type": "CITIZEN", "description": "Large fire reported near Block A with smoke visible", "location_name": "Block A", "latitude": 11.0168, "longitude": 76.9558, "reported_at": "2026-09-23T10:30:00Z"}
    payload.update(overrides)
    return payload
