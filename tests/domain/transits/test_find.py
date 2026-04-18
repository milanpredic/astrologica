"""find_transits — range search for exact transit crossings."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from astrologica.aspect import AspectKind
from astrologica.chart import compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.swisseph import SwissEphemerisAdapter
from astrologica.transits import find_transits

pytestmark = pytest.mark.infrastructure


@pytest.fixture
def natal_at_j2000() -> ChartData:
    return ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=0.0, longitude=0.0),
    )


class TestFindTransits:
    def test_empty_window_returns_empty_tuple(self, natal_at_j2000) -> None:
        natal = compute_natal_chart(natal_at_j2000, ephemeris=SwissEphemerisAdapter())
        start = datetime(2001, 1, 1, tzinfo=UTC)
        result = find_transits(natal, start=start, end=start, ephemeris=SwissEphemerisAdapter())
        assert result == ()

    def test_moon_conjunct_natal_sun_found_within_a_month(self, natal_at_j2000) -> None:
        """The moon transits every natal placement every ~27d. Find a conjunction."""
        natal = compute_natal_chart(natal_at_j2000, ephemeris=SwissEphemerisAdapter())
        start = datetime(2001, 3, 1, tzinfo=UTC)
        end = start + timedelta(days=35)
        events = find_transits(
            natal,
            start=start,
            end=end,
            transiting_bodies=[Planet.MOON],
            natal_bodies=[Planet.SUN],
            aspects=[AspectKind.CONJUNCTION],
            ephemeris=SwissEphemerisAdapter(),
        )
        assert any(
            e.transiting is Planet.MOON
            and e.natal is Planet.SUN
            and e.kind is AspectKind.CONJUNCTION
            for e in events
        )
        # At most two such conjunctions in a 35-day window (one full lunar cycle + a bit).
        assert len(events) <= 2

    def test_events_are_sorted_by_time(self, natal_at_j2000) -> None:
        natal = compute_natal_chart(natal_at_j2000, ephemeris=SwissEphemerisAdapter())
        start = datetime(2001, 3, 1, tzinfo=UTC)
        end = start + timedelta(days=30)
        events = find_transits(
            natal,
            start=start,
            end=end,
            transiting_bodies=[Planet.MOON],
            ephemeris=SwissEphemerisAdapter(),
        )
        times = [e.when for e in events]
        assert times == sorted(times)
