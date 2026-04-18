"""Composition tests — tradition + ayanamsa + frame interact correctly.

Also verifies `Chart.to_dict()` exposes the new fields so callers can
JSON-serialize the chart without losing configuration.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from astrologica.chart import ChartTradition, compute_natal_chart
from astrologica.chart_data import Ayanamsa, ChartData, ReferenceFrame
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.swisseph import SwissEphemerisAdapter

pytestmark = pytest.mark.infrastructure


@pytest.fixture
def j2000() -> ChartData:
    return ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=40.0, longitude=-74.0, altitude=10.0),
    )


class TestTraditionAyanamsaFrameCompose:
    def test_modern_plus_lahiri_plus_topocentric_all_apply(self, j2000) -> None:
        """All three parameters change the output — together they compose."""
        data = ChartData(
            datetime=j2000.datetime,
            place=j2000.place,
            ayanamsa=Ayanamsa.LAHIRI,
            frame=ReferenceFrame.TOPOCENTRIC,
        )
        chart = compute_natal_chart(
            data,
            ephemeris=SwissEphemerisAdapter(),
            tradition=ChartTradition.MODERN,
        )

        # Tradition applied → modern bodies present.
        assert chart.tradition is ChartTradition.MODERN
        assert Planet.URANUS in chart.planets
        assert Planet.TRUE_NODE in chart.planets

        # Ayanamsa applied → Sun longitude differs from tropical reference
        # (~280.37° at J2000) by ~23.85° (Lahiri).
        sun_lon = float(chart.planets[Planet.SUN].longitude)
        tropical = 280.37
        shift = (tropical - sun_lon) % 360.0
        assert 23.0 < shift < 25.0

        # Frame applied → topocentric Moon differs from geocentric.
        geo_data = ChartData(datetime=j2000.datetime, place=j2000.place, ayanamsa=Ayanamsa.LAHIRI)
        geo_chart = compute_natal_chart(
            geo_data,
            ephemeris=SwissEphemerisAdapter(),
            tradition=ChartTradition.MODERN,
        )
        moon_topo = float(chart.planets[Planet.MOON].longitude)
        moon_geo = float(geo_chart.planets[Planet.MOON].longitude)
        delta = abs((moon_topo - moon_geo + 180.0) % 360.0 - 180.0)
        # Parallax should be non-zero but small (< 2°).
        assert 0.0 < delta < 2.0

    def test_chart_data_preserves_all_three_parameters(self, j2000) -> None:
        """Chart data echoes back what was passed in (for traceability)."""
        data = ChartData(
            datetime=j2000.datetime,
            place=j2000.place,
            ayanamsa=Ayanamsa.FAGAN_BRADLEY,
            frame=ReferenceFrame.HELIOCENTRIC,
        )
        chart = compute_natal_chart(
            data, ephemeris=SwissEphemerisAdapter(), tradition=ChartTradition.MODERN
        )
        assert chart.data.ayanamsa is Ayanamsa.FAGAN_BRADLEY
        assert chart.data.frame is ReferenceFrame.HELIOCENTRIC
        assert chart.tradition is ChartTradition.MODERN


class TestChartToDictNewFields:
    def test_to_dict_includes_tradition(self, j2000) -> None:
        chart = compute_natal_chart(
            j2000, ephemeris=SwissEphemerisAdapter(), tradition=ChartTradition.MODERN
        )
        d = chart.to_dict()
        assert d["tradition"] == "MODERN"

    def test_to_dict_round_trips_through_json(self, j2000) -> None:
        """All fields (including new ones) are JSON-serialisable without loss."""
        data = ChartData(
            datetime=j2000.datetime,
            place=j2000.place,
            ayanamsa=Ayanamsa.LAHIRI,
        )
        chart = compute_natal_chart(
            data,
            ephemeris=SwissEphemerisAdapter(),
            tradition=ChartTradition.MODERN,
        )
        blob = json.dumps(chart.to_dict())
        parsed = json.loads(blob)
        # Sanity: the new fields survive the round-trip.
        assert parsed["tradition"] == "MODERN"
        assert "syzygy" in parsed
        assert "planets" in parsed
        # Modern-tradition chart has 14 planets in the dict.
        assert len(parsed["planets"]) == 14

    def test_to_dict_syzygy_has_kind_and_when(self, j2000) -> None:
        chart = compute_natal_chart(j2000, ephemeris=SwissEphemerisAdapter())
        d = chart.to_dict()
        assert d["syzygy"]["kind"] in ("NEW_MOON", "FULL_MOON")
        assert "when" in d["syzygy"]
        assert "longitude" in d["syzygy"]
