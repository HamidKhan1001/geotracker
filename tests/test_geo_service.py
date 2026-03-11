"""
Tests for app/geo_service.py
Run with: pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock
from app.geo_service import lookup, GeoServiceError, GeoResult, _is_private_ip


# ── Fixtures ──────────────────────────────────────────────────────────────────

MOCK_RESPONSE = {
    "ip": "8.8.8.8",
    "city": "Mountain View",
    "region": "California",
    "country_name": "United States",
    "country_code": "US",
    "postal": "94043",
    "latitude": 37.4056,
    "longitude": -122.0775,
    "timezone": "America/Los_Angeles",
    "org": "AS15169 Google LLC",
    "asn": "AS15169",
}


def _make_mock_response(data: dict, status_code: int = 200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        from requests.exceptions import HTTPError
        mock.raise_for_status.side_effect = HTTPError(response=mock)
    return mock


# ── Unit Tests: _is_private_ip ────────────────────────────────────────────────

class TestIsPrivateIp:
    def test_loopback(self):
        assert _is_private_ip("127.0.0.1") is True

    def test_class_a_private(self):
        assert _is_private_ip("10.0.0.1") is True

    def test_class_c_private(self):
        assert _is_private_ip("192.168.1.1") is True

    def test_public_ip(self):
        assert _is_private_ip("8.8.8.8") is False

    def test_another_public_ip(self):
        assert _is_private_ip("1.1.1.1") is False

    def test_localhost_string(self):
        assert _is_private_ip("localhost") is True


# ── Unit Tests: lookup() ──────────────────────────────────────────────────────

class TestLookup:

    @patch("app.geo_service.requests.get")
    def test_successful_lookup(self, mock_get):
        mock_get.return_value = _make_mock_response(MOCK_RESPONSE)
        result = lookup("8.8.8.8")

        assert isinstance(result, GeoResult)
        assert result.ip == "8.8.8.8"
        assert result.city == "Mountain View"
        assert result.country == "United States"
        assert result.country_code == "US"
        assert result.latitude == pytest.approx(37.4056)
        assert result.longitude == pytest.approx(-122.0775)
        assert result.timezone == "America/Los_Angeles"
        assert result.org == "AS15169 Google LLC"

    @patch("app.geo_service.requests.get")
    def test_lookup_no_ip_uses_caller(self, mock_get):
        mock_get.return_value = _make_mock_response(MOCK_RESPONSE)
        lookup(None)
        call_url = mock_get.call_args[0][0]
        assert call_url == "https://ipapi.co/json/"

    @patch("app.geo_service.requests.get")
    def test_lookup_with_ip_uses_ip_url(self, mock_get):
        mock_get.return_value = _make_mock_response(MOCK_RESPONSE)
        lookup("8.8.8.8")
        call_url = mock_get.call_args[0][0]
        assert "8.8.8.8" in call_url

    def test_private_ip_raises(self):
        with pytest.raises(GeoServiceError, match="private"):
            lookup("192.168.1.1")

    def test_loopback_ip_raises(self):
        with pytest.raises(GeoServiceError, match="private"):
            lookup("127.0.0.1")

    @patch("app.geo_service.requests.get")
    def test_api_error_field_raises(self, mock_get):
        mock_get.return_value = _make_mock_response({"error": True, "reason": "Invalid IP"})
        with pytest.raises(GeoServiceError, match="Invalid IP"):
            lookup("999.999.999.999")

    @patch("app.geo_service.requests.get")
    def test_missing_coordinates_raises(self, mock_get):
        bad_data = {**MOCK_RESPONSE, "latitude": None, "longitude": None}
        mock_get.return_value = _make_mock_response(bad_data)
        with pytest.raises(GeoServiceError, match="coordinates"):
            lookup("8.8.8.8")

    @patch("app.geo_service.requests.get")
    def test_connection_error_raises(self, mock_get):
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError()
        with pytest.raises(GeoServiceError, match="internet connection"):
            lookup("8.8.8.8")

    @patch("app.geo_service.requests.get")
    def test_timeout_raises(self, mock_get):
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()
        with pytest.raises(GeoServiceError, match="timed out"):
            lookup("8.8.8.8")

    @patch("app.geo_service.requests.get")
    def test_http_error_raises(self, mock_get):
        from requests.exceptions import HTTPError
        mock_get.side_effect = HTTPError()
        with pytest.raises(GeoServiceError, match="API returned error"):
            lookup("8.8.8.8")

    @patch("app.geo_service.requests.get")
    def test_invalid_json_raises(self, mock_get):
        mock = MagicMock()
        mock.raise_for_status = MagicMock()
        mock.json.side_effect = ValueError("bad json")
        mock_get.return_value = mock
        with pytest.raises(GeoServiceError, match="JSON"):
            lookup("8.8.8.8")


# ── Unit Tests: GeoResult ─────────────────────────────────────────────────────

class TestGeoResult:

    def _make_result(self, **kwargs):
        defaults = dict(
            ip="8.8.8.8", city="Mountain View", region="California",
            country="United States", country_code="US", postal="94043",
            latitude=37.4056, longitude=-122.0775,
            timezone="America/Los_Angeles", org="Google LLC", asn="AS15169"
        )
        return GeoResult(**{**defaults, **kwargs})

    def test_to_dict_has_all_fields(self):
        r = self._make_result()
        d = r.to_dict()
        assert "ip" in d
        assert "latitude" in d
        assert "longitude" in d
        assert "city" in d

    def test_display_location_full(self):
        r = self._make_result()
        assert r.display_location == "Mountain View, California, United States"

    def test_display_location_city_only(self):
        r = self._make_result(region="", country="")
        assert r.display_location == "Mountain View"

    def test_display_location_all_empty(self):
        r = self._make_result(city="", region="", country="")
        assert r.display_location == "Unknown"
