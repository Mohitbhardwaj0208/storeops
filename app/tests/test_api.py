"""Basic tests - run with: pytest app/tests"""
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import main


def test_health_reports_db_down_when_connection_fails():
    with patch.object(main, "get_conn", side_effect=Exception("boom")):
        client = TestClient(main.app, raise_server_exceptions=False)
        with patch.object(main, "init_db"):
            r = client.get("/health")
    assert r.status_code == 503


def test_heartbeat_unknown_store_returns_404():
    fake_cur = MagicMock()
    fake_cur.fetchone.return_value = None
    fake_conn = MagicMock()
    fake_conn.__enter__.return_value.execute.return_value = fake_cur
    with patch.object(main, "get_conn", return_value=fake_conn), patch.object(main, "init_db"):
        client = TestClient(main.app)
        r = client.post("/stores/NOPE/heartbeat")
    assert r.status_code == 404
