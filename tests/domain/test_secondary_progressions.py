"""Secondary progressions — day-for-year progressed chart."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from astrologica.chart import compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.secondary_progressions import compute_secondary_progressions
from astrologica.swisseph import SwissEphemerisAdapter

pytestmark = pytest.mark.infrastructure


@pytest.fixture
def natal() -> ChartData:
    return ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=0.0, longitude=0.0),
    )


class TestSecondaryProgressions:
    def test_moves_forward_by_age_days(self, natal) -> None:
        natal_chart = compute_natal_chart(natal, ephemeris=SwissEphemerisAdapter())
        prog = compute_secondary_progressions(
            natal_chart, age_years=10, ephemeris=SwissEphemerisAdapter()
        )
        expected = natal.datetime + timedelta(days=10)
        assert prog.data.datetime == expected

    def test_progressed_sun_moves_approximately_one_degree_per_year(self, natal) -> None:
        natal_chart = compute_natal_chart(natal, ephemeris=SwissEphemerisAdapter())
        prog = compute_secondary_progressions(
            natal_chart, age_years=5, ephemeris=SwissEphemerisAdapter()
        )
        natal_sun = float(natal_chart.planets[Planet.SUN].longitude)
        prog_sun = float(prog.planets[Planet.SUN].longitude)
        delta = abs((prog_sun - natal_sun + 180.0) % 360.0 - 180.0)
        # Sun moves ~1°/day → progressed Sun moves ~5° in 5 years (± small seasonal variance).
        assert 4.0 < delta < 6.0, f"progressed sun Δ = {delta}°"

    def test_zero_years_is_natal_chart(self, natal) -> None:
        natal_chart = compute_natal_chart(natal, ephemeris=SwissEphemerisAdapter())
        prog = compute_secondary_progressions(
            natal_chart, age_years=0, ephemeris=SwissEphemerisAdapter()
        )
        # Positions should match exactly.
        for p in Planet.classical():
            natal_lon = float(natal_chart.planets[p].longitude)
            prog_lon = float(prog.planets[p].longitude)
            assert natal_lon == pytest.approx(prog_lon, abs=1e-9)

    def test_negative_age_rejected(self, natal) -> None:
        natal_chart = compute_natal_chart(natal, ephemeris=SwissEphemerisAdapter())
        with pytest.raises(ValueError):
            compute_secondary_progressions(
                natal_chart, age_years=-1, ephemeris=SwissEphemerisAdapter()
            )
