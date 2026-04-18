"""SwissEphemerisAdapter integration test against hand-verified reference values.

Reference chart: J2000.0 — 2000-01-01T12:00:00Z at Greenwich (0° N, 0° E).
Published Moshier ephemeris values (pyswisseph FLG_MOSEPH) for this moment are
well-known; we assert planetary longitudes within 0.01° and ASC/MC within 0.02°.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica.chart import ChartTradition, compute_natal_chart
from astrologica.chart_data import Ayanamsa, ChartData, ReferenceFrame
from astrologica.house import HouseSystem
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.swisseph import SwissEphemerisAdapter

pytestmark = pytest.mark.infrastructure


@pytest.fixture
def j2000_data() -> ChartData:
    return ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=0.0, longitude=0.0),
    )


class TestSwissEphemerisAdapter:
    def test_planet_longitudes_match_reference(self, j2000_data: ChartData) -> None:
        """At J2000.0 the Sun is near 280.4°; other planets similarly well-known."""
        adapter = SwissEphemerisAdapter()
        chart = compute_natal_chart(
            j2000_data, house_system=HouseSystem.REGIOMONTANUS, ephemeris=adapter
        )

        # Reference values from pyswisseph (FLG_MOSEPH) at JD 2451545.0 — these are
        # the Moshier-ephemeris apparent geocentric longitudes that the adapter returns
        # when queried directly; pinning them here guards against regressions in the
        # adapter's unit handling (flags, signs, Swiss vs Moshier, etc.).
        expected_longitudes = {
            Planet.SUN: 280.3689,
            Planet.MOON: 223.3238,
            Planet.MERCURY: 271.8893,
            Planet.VENUS: 241.5658,
            Planet.MARS: 327.9633,
            Planet.JUPITER: 25.2530,
            Planet.SATURN: 40.3956,
        }
        for planet, expected in expected_longitudes.items():
            actual = chart.planets[planet].longitude
            diff = abs(((actual - expected) + 180.0) % 360.0 - 180.0)
            assert (
                diff < 0.01
            ), f"{planet.name}: expected ≈{expected}°, got {actual:.4f}° (diff {diff:.4f}°)"

    def test_ascendant_midheaven_at_greenwich_j2000(self, j2000_data: ChartData) -> None:
        adapter = SwissEphemerisAdapter()
        chart = compute_natal_chart(
            j2000_data, house_system=HouseSystem.REGIOMONTANUS, ephemeris=adapter
        )
        # pyswisseph (Moshier) reference at Greenwich J2000 noon:
        #   ASC = 11.3739°, MC = 279.6111°
        assert float(chart.ascendant) == pytest.approx(11.3739, abs=0.01)
        assert float(chart.midheaven) == pytest.approx(279.6111, abs=0.01)

    def test_full_pipeline_produces_valid_chart(self, j2000_data: ChartData) -> None:
        """End-to-end smoke: chart is complete and serialisable."""
        import json

        chart = compute_natal_chart(j2000_data, ephemeris=SwissEphemerisAdapter())
        assert len(chart.planets) == 7
        assert len(chart.houses) == 12
        assert len(chart.lots) == 7
        assert chart.syzygy.kind.name in ("NEW_MOON", "FULL_MOON")
        # Round-trip to JSON
        json.dumps(chart.to_dict())

    def test_modern_chart_includes_outers_and_nodes(self, j2000_data: ChartData) -> None:
        """MODERN tradition adds Uranus/Neptune/Pluto + four node members."""
        chart = compute_natal_chart(
            j2000_data,
            ephemeris=SwissEphemerisAdapter(),
            tradition=ChartTradition.MODERN,
        )
        assert len(chart.planets) == 14

        for p in (Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO):
            assert p in chart.planets

    def test_sidereal_longitude_differs_from_tropical_by_ayanamsa(
        self, j2000_data: ChartData
    ) -> None:
        """Lahiri ayanamsa shifts all tropical longitudes by ~23.85° (at J2000)."""
        tropical = compute_natal_chart(j2000_data, ephemeris=SwissEphemerisAdapter())
        sidereal_data = ChartData(
            datetime=j2000_data.datetime,
            place=j2000_data.place,
            ayanamsa=Ayanamsa.LAHIRI,
        )
        sidereal = compute_natal_chart(sidereal_data, ephemeris=SwissEphemerisAdapter())

        # Lahiri ayanamsa at J2000 is ~23.85°. The sidereal longitude equals
        # tropical − ayanamsa. Check for several bodies that the shift is consistent.
        shifts = []
        for p in (Planet.SUN, Planet.MOON, Planet.JUPITER):
            diff = (
                float(tropical.planets[p].longitude) - float(sidereal.planets[p].longitude)
            ) % 360.0
            shifts.append(diff)
        assert all(23.0 < s < 25.0 for s in shifts), f"Lahiri shift out of range: {shifts}"
        assert max(shifts) - min(shifts) < 0.01, f"shifts not consistent: {shifts}"

    def test_tropical_output_unchanged_when_ayanamsa_is_none(self, j2000_data: ChartData) -> None:
        """Default (no ayanamsa) must produce identical output to explicitly-tropical."""
        a = compute_natal_chart(j2000_data, ephemeris=SwissEphemerisAdapter())
        b = compute_natal_chart(
            ChartData(datetime=j2000_data.datetime, place=j2000_data.place, ayanamsa=None),
            ephemeris=SwissEphemerisAdapter(),
        )
        assert float(a.planets[Planet.SUN].longitude) == pytest.approx(
            float(b.planets[Planet.SUN].longitude), abs=1e-9
        )

    def test_topocentric_moon_differs_from_geocentric(self, j2000_data: ChartData) -> None:
        """Topocentric Moon position differs from geocentric by up to ~1° (parallax)."""
        geo = compute_natal_chart(j2000_data, ephemeris=SwissEphemerisAdapter())

        topo_data = ChartData(
            datetime=j2000_data.datetime,
            place=Place(latitude=0.0, longitude=0.0, altitude=0.0),
            frame=ReferenceFrame.TOPOCENTRIC,
        )
        topo = compute_natal_chart(topo_data, ephemeris=SwissEphemerisAdapter())

        geo_moon = float(geo.planets[Planet.MOON].longitude)
        topo_moon = float(topo.planets[Planet.MOON].longitude)
        delta = abs((geo_moon - topo_moon + 180.0) % 360.0 - 180.0)
        # Parallax at Greenwich J2000 noon — expect a modest but non-zero shift.
        assert 0.0 < delta < 2.0, f"topocentric Moon shift out of range: {delta}°"

    def test_heliocentric_sun_is_near_zero_longitude(self, j2000_data: ChartData) -> None:
        """From the Sun's own frame, the Sun's longitude collapses to ~0°."""
        helio_data = ChartData(
            datetime=j2000_data.datetime,
            place=j2000_data.place,
            frame=ReferenceFrame.HELIOCENTRIC,
        )
        chart = compute_natal_chart(helio_data, ephemeris=SwissEphemerisAdapter())
        sun_lon = float(chart.planets[Planet.SUN].longitude)
        # "near 0°" = within a degree of either 0 or 360 (wrapping).
        wrapped = min(sun_lon, 360.0 - sun_lon)
        assert wrapped < 1.0, f"heliocentric Sun expected ~0°, got {sun_lon}°"

    def test_south_nodes_are_antipodal_to_north_nodes(self, j2000_data: ChartData) -> None:
        """South node longitudes are exactly 180° from their north-node counterparts."""
        chart = compute_natal_chart(
            j2000_data,
            ephemeris=SwissEphemerisAdapter(),
            tradition=ChartTradition.MODERN,
        )
        true_n = chart.planets[Planet.TRUE_NODE].longitude
        south_true = chart.planets[Planet.SOUTH_TRUE_NODE].longitude
        assert ((south_true - true_n) % 360.0) == pytest.approx(180.0, abs=1e-9)

        mean_n = chart.planets[Planet.MEAN_NODE].longitude
        south_mean = chart.planets[Planet.SOUTH_MEAN_NODE].longitude
        assert ((south_mean - mean_n) % 360.0) == pytest.approx(180.0, abs=1e-9)
