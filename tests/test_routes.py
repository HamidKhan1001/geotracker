"""
Tests for Flask API routes.
Run with: pytest tests/ -v
"""

import pytest
from unittest.mock import patch
from app.routes import create_app
from app.geo_service import GeoResult, GeoServiceError


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


MOCK_RESULT = GeoResult(
    ip="8.8.8.8", city="Mountain View", region="California",
    country="United States", country_code="US", postal="94043",
    latitude=37.4056, longitude=-122.0775,
    timezone="America/Los_Angeles", org="Google LLC", asn="AS15169"
)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.get_json()["status"] == "ok"

    def test_health_returns_version(self, client):
        r = client.get("/health")
        assert "version" in r.get_json()


class TestLookupEndpoint:

    @patch("app.routes.build_map_html", return_value="<iframe></iframe>")
    @patch("app.routes.lookup", return_value=MOCK_RESULT)
    def test_lookup_with_ip(self, mock_lookup, mock_map, client):
        r = client.get("/api/lookup?ip=8.8.8.8")
        assert r.status_code == 200
        body = r.get_json()
        assert body["ok"] is True
        assert body["data"]["ip"] == "8.8.8.8"
        assert body["data"]["city"] == "Mountain View"
        assert "map_html" in body
        mock_lookup.assert_called_once_with("8.8.8.8")

    @patch("app.routes.build_map_html", return_value="<iframe></iframe>")
    @patch("app.routes.lookup", return_value=MOCK_RESULT)
    def test_lookup_no_ip(self, mock_lookup, mock_map, client):
        r = client.get("/api/lookup")
        assert r.status_code == 200
        mock_lookup.assert_called_once_with(None)

    @patch("app.routes.lookup", side_effect=GeoServiceError("Invalid IP address"))
    def test_lookup_service_error(self, mock_lookup, client):
        r = client.get("/api/lookup?ip=bad_ip")
        assert r.status_code == 400
        body = r.get_json()
        assert body["ok"] is False
        assert "Invalid IP" in body["error"]

    @patch("app.routes.lookup", side_effect=Exception("Something broke"))
    def test_lookup_unexpected_error(self, mock_lookup, client):
        r = client.get("/api/lookup?ip=1.2.3.4")
        assert r.status_code == 500
        body = r.get_json()
        assert body["ok"] is False


class TestIndexEndpoint:
    def test_index_returns_html(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert b"GeoTracker" in r.data
        assert b"Track IP" in r.data
