import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil

from app.main import app
from app.db.database import Base, engine, init_db

SAMPLE_PROJECTS = Path(__file__).parent.parent.parent / "sample-projects"


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_version_endpoint(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_list_vulnerabilities(client):
    response = client.get("/api/vulnerabilities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_list_vulnerabilities_filter_ecosystem(client):
    response = client.get("/api/vulnerabilities?ecosystem=python")
    assert response.status_code == 200
    data = response.json()
    assert all(v["ecosystem"] == "python" for v in data)


def test_list_scans_empty(client):
    response = client.get("/api/scans")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.skipif(not (SAMPLE_PROJECTS / "python-vulnerable").exists(), reason="sample projects not available")
def test_create_scan(client):
    payload = {"project_path": str(SAMPLE_PROJECTS / "python-vulnerable")}
    response = client.post("/api/scans", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "scan_id" in data
    assert data["total_dependencies"] > 0

    scan_id = data["scan_id"]
    detail = client.get(f"/api/scans/{scan_id}")
    assert detail.status_code == 200
    assert detail.json()["scan_id"] == scan_id


def test_create_scan_invalid_path(client):
    payload = {"project_path": "/absolutely/nonexistent/path"}
    response = client.post("/api/scans", json=payload)
    assert response.status_code == 400


def test_get_nonexistent_scan(client):
    response = client.get("/api/scans/nonexistent-id-12345")
    assert response.status_code == 404
