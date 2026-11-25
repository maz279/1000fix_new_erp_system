"""INT-020 / INT-022 primary-path and fallback tests for GeospatialClient (CD-M02-06).

The OSRM HTTP call is mocked; nothing here touches the network.
"""

import json
import logging
import sys
import urllib.error
from pathlib import Path

import pytest

_service_root = Path(__file__).resolve().parents[1]
if str(_service_root) not in sys.path:
    sys.path.insert(0, str(_service_root))

from dispatch_scoring import geospatial_client
from dispatch_scoring.geospatial_client import GeospatialClient


class _FakeResponse:
    def __init__(self, status, body):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _install_urlopen(monkeypatch, status=200, payload=None, raises=None):
    calls = []

    def fake_urlopen(req, timeout):
        calls.append((req, timeout))
        if raises is not None:
            raise raises
        body = json.dumps(payload if payload is not None else {}).encode()
        return _FakeResponse(status, body)

    monkeypatch.setattr(geospatial_client.urllib.request, "urlopen", fake_urlopen)
    return calls


START = (23.7644, 90.3928)
END = (23.7937, 90.4066)


def test_osrm_primary_route_is_used_when_available(monkeypatch):
    calls = _install_urlopen(
        monkeypatch,
        payload={"code": "Ok", "routes": [{"distance": 4321.0, "duration": 612.0}]},
    )
    client = GeospatialClient(osrm_url="http://osrm.test:5000")
    res = client.route_eta(*START, *END)

    assert res.source == "osrm_primary"
    assert res.distance_km == 4.32
    assert res.duration_min == 10.2
    assert res.start == START
    assert res.end == END
    req, timeout = calls[0]
    # OSRM expects lon,lat ordering
    assert req.full_url == (
        "http://osrm.test:5000/route/v1/driving/90.3928,23.7644;90.4066,23.7937?overview=false"
    )
    assert req.get_header("User-agent") == "1000FiX-ERP/1.0"
    assert timeout == 1.5


@pytest.mark.parametrize(
    ("status", "payload"),
    [
        (200, {"code": "NoRoute", "routes": []}),
        (200, {"code": "Ok", "routes": []}),
        (503, {"code": "Ok", "routes": [{"distance": 1.0, "duration": 1.0}]}),
    ],
)
def test_unusable_osrm_answers_fall_back_to_haversine(monkeypatch, status, payload):
    _install_urlopen(monkeypatch, status=status, payload=payload)
    res = GeospatialClient(osrm_url="http://osrm.test:5000").route_eta(*START, *END)
    assert res.source == "haversine_fallback"
    expected_km = GeospatialClient._haversine_km(*START, *END)
    assert res.distance_km == round(expected_km, 2)
    assert res.duration_min == round((expected_km / 18.0) * 60.0 * 1.6, 1)


def test_osrm_error_is_logged_and_falls_back(monkeypatch, caplog):
    _install_urlopen(monkeypatch, raises=urllib.error.URLError("connection refused"))
    with caplog.at_level(logging.DEBUG, logger=geospatial_client.logger.name):
        res = GeospatialClient(osrm_url="http://osrm.test:5000").route_eta(*START, *END)
    assert res.source == "haversine_fallback"
    assert "OSRM routing unavailable" in caplog.text
    assert "connection refused" in caplog.text


def test_endpoints_come_from_environment(monkeypatch):
    monkeypatch.setenv("OSRM_URL", "http://osrm.env:1")
    monkeypatch.setenv("VROOM_URL", "http://vroom.env:2")
    monkeypatch.setenv("TRACCAR_URL", "http://traccar.env:3")
    client = GeospatialClient()
    assert (client.osrm_url, client.vroom_url, client.traccar_url) == (
        "http://osrm.env:1",
        "http://vroom.env:2",
        "http://traccar.env:3",
    )


@pytest.mark.parametrize(
    ("hour", "expected"),
    [
        (7, 1.05),
        (8, 1.95),
        (11, 1.95),
        (12, 1.45),
        (16, 1.45),
        (17, 2.20),
        (20, 2.20),
        (21, 1.05),
    ],
)
def test_traffic_multiplier_curve(hour, expected):
    res = GeospatialClient().get_traffic_multiplier("DHAKA-NORTH", hour)
    assert res.congestion_multiplier == expected
    assert (res.zone, res.hour, res.source) == ("DHAKA-NORTH", hour, "statistical_model")


def test_geocode_known_hub_is_case_insensitive():
    res = GeospatialClient().geocode("road 11, chattogram")
    assert (res.latitude, res.longitude) == (22.3569, 91.7832)
    assert res.accuracy == "district_centroid"
