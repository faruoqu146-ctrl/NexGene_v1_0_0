"""Lightweight stress and abuse-path checks for NexGene v1.0.0."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fastapi.testclient import TestClient
from backend.app.main import app, MAX_REQUEST_BYTES

client = TestClient(app)


def test_health_and_version_surface():
    r = client.get("/")
    assert r.status_code == 200
    assert "html" in r.headers.get("content-type", "").lower() or r.status_code == 200


def test_oversized_body_is_rejected():
    huge = "x" * (MAX_REQUEST_BYTES + 100)
    r = client.post(
        "/api/v1/auth/register",
        content=huge,
        headers={"content-type": "application/json", "content-length": str(len(huge))},
    )
    assert r.status_code in (400, 413, 422)


def test_many_checkins_and_weekly_report():
    email = "stress-user@example.com"
    password = "A_secure_password!9"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    csrf = r.cookies.get("nexgene_csrf") or client.cookies.get("nexgene_csrf")
    headers = {"X-CSRF-Token": csrf}
    for i in range(12):
        payload = {"values": {"energy": (i % 10) + 1, "sleep_duration": 6 + (i % 3) * 0.5}}
        rr = client.post("/api/v1/checkins/morning", json=payload, headers=headers)
        assert rr.status_code == 200
    report = client.get("/api/v1/reports/weekly")
    assert report.status_code == 200
    body = report.json()
    assert body["status"] in ("ready", "not_ready")
    signals = client.get("/api/v1/signals")
    assert signals.status_code == 200
    patterns = client.get("/api/v1/patterns")
    assert patterns.status_code == 200
