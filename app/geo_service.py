"""
Service layer — all geolocation business logic lives here.
Clean separation from Flask routes so it's fully testable.
"""

import requests
import logging
from dataclasses import dataclass, asdict
from typing import Optional
from app.config import Config

logger = logging.getLogger(__name__)


class GeoServiceError(Exception):
    pass


@dataclass
class GeoResult:
    ip: str
    city: str
    region: str
    country: str
    country_code: str
    postal: str
    latitude: float
    longitude: float
    timezone: str
    org: str
    asn: str
    is_private: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def display_location(self) -> str:
        parts = [p for p in [self.city, self.region, self.country] if p]
        return ", ".join(parts) or "Unknown"


def _is_private_ip(ip: str) -> bool:
    private_prefixes = ("10.", "192.168.", "127.", "::1", "localhost")
    return ip.startswith(private_prefixes)


def lookup(ip: Optional[str] = None) -> GeoResult:
    if ip and _is_private_ip(ip):
        raise GeoServiceError(f"'{ip}' is a private/local IP address — not routable on the internet.")

    target = ip if ip else ""
    url = f"http://ip-api.com/json/{target}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    logger.info("Querying %s", url)

    try:
        resp = requests.get(url, timeout=Config.REQUEST_TIMEOUT, headers={"User-Agent": "GeoTracker/1.0"})
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        raise GeoServiceError("Cannot reach geolocation service. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise GeoServiceError(f"Request timed out after {Config.REQUEST_TIMEOUT}s.")
    except requests.exceptions.HTTPError as e:
        raise GeoServiceError(f"API returned error: {e}")
    except ValueError:
        raise GeoServiceError("Invalid JSON response from API.")

    if data.get("status") == "fail":
        raise GeoServiceError(data.get("message", "IP lookup failed."))

    if not data.get("lat") or not data.get("lon"):
        raise GeoServiceError("No coordinates returned — IP may be unresolvable.")

    return GeoResult(
        ip=data.get("query", ip or "unknown"),
        city=data.get("city") or "",
        region=data.get("regionName") or "",
        country=data.get("country") or "",
        country_code=data.get("countryCode") or "",
        postal=data.get("zip") or "",
        latitude=float(data["lat"]),
        longitude=float(data["lon"]),
        timezone=data.get("timezone") or "",
        org=data.get("isp") or data.get("org") or "",
        asn=data.get("as") or "",
    )
