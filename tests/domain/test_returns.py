"""Solar and lunar returns — integration tests against Swiss Ephemeris."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from astrologica.chart import compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.returns import compute_lunar_return, compute_solar_return
from astrologica.swisseph import SwissEphemerisAdapter

pytestmark = pytest.mark.infrastructure


@pytest.fixture
def j2000_natal() -> ChartData:
    return ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=0.0, longitude=0.0),
    )


class TestSolarReturn:
    def test_sun_longitude_matches_natal_at_return(self, j2000_natal) -> None:
        natal = compute_natal_chart(j2000_natal, ephemeris=SwissEphemerisAdapter())
        sr = compute_solar_return(natal, year=2005, ephemeris=SwissEphemerisAdapter())
        natal_sun = float(natal.planets[Planet.SUN].longitude)
        sr_sun = float(sr.planets[Planet.SUN].longitude)
        diff = abs((sr_sun - natal_sun + 180.0) % 360.0 - 180.0)
        assert diff < 0.001, f"SR Sun {sr_sun}° differs from natal {natal_sun}° by {diff}°"

    def test_return_occurs_within_two_days_of_birthday(self, j2000_natal) -> None:
        natal = compute_natal_chart(j2000_natal, ephemeris=SwissEphemerisAdapter())
        sr = compute_solar_return(natal, year=2005, ephemeris=SwissEphemerisAdapter())
        target = datetime(2005, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert abs((sr.data.datetime - target).total_seconds()) < 2 * 86400


class TestLunarReturn:
    def test_moon_longitude_matches_natal_at_return(self, j2000_natal) -> None:
        natal = compute_natal_chart(j2000_natal, ephemeris=SwissEphemerisAdapter())
        after = datetime(2005, 3, 1, tzinfo=UTC)
        lr = compute_lunar_return(natal, after=after, ephemeris=SwissEphemerisAdapter())
        natal_moon = float(natal.planets[Planet.MOON].longitude)
        lr_moon = float(lr.planets[Planet.MOON].longitude)
        diff = abs((lr_moon - natal_moon + 180.0) % 360.0 - 180.0)
        assert diff < 0.01, f"LR Moon {lr_moon}° differs from natal {natal_moon}° by {diff}°"

    def test_lunar_return_happens_within_28_days_of_after(self, j2000_natal) -> None:
        natal = compute_natal_chart(j2000_natal, ephemeris=SwissEphemerisAdapter())
        after = datetime(2005, 3, 1, tzinfo=UTC)
        lr = compute_lunar_return(natal, after=after, ephemeris=SwissEphemerisAdapter())
        assert lr.data.datetime >= after - timedelta(days=1)
        assert lr.data.datetime <= after + timedelta(days=28)
