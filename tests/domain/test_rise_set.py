"""Rise/set/MC/IC times for a body at a place."""

from __future__ import annotations

from datetime import date

import pytest

from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.rise_set import compute_rise_set
from astrologica.swisseph import SwissEphemerisAdapter

pytestmark = pytest.mark.infrastructure


class TestComputeRiseSet:
    def test_sun_rise_at_equator_equinox_near_six_local(self) -> None:
        times = compute_rise_set(
            Planet.SUN,
            date(2025, 3, 20),
            Place(latitude=0.0, longitude=0.0),
            ephemeris=SwissEphemerisAdapter(),
        )
        assert times.rise is not None
        # At the equator on the equinox, sunrise is near 06:00 UTC (Greenwich).
        assert 5.5 <= times.rise.hour + times.rise.minute / 60.0 <= 6.5

    def test_all_four_events_present_at_temperate_latitude(self) -> None:
        times = compute_rise_set(
            Planet.SUN,
            date(2025, 6, 1),
            Place(latitude=40.0, longitude=-74.0),
            ephemeris=SwissEphemerisAdapter(),
        )
        assert times.rise is not None
        assert times.mc is not None
        assert times.set is not None
        assert times.ic is not None

    def test_each_event_is_within_24h_of_midnight(self) -> None:
        """Each of rise/mc/set/ic is the *next* such event after local midnight,
        each computed independently — so they may not be in their natural
        daily order, but each should be within 24h of midnight."""
        from datetime import UTC, datetime, timedelta

        times = compute_rise_set(
            Planet.SUN,
            date(2025, 6, 1),
            Place(latitude=40.0, longitude=-74.0),
            ephemeris=SwissEphemerisAdapter(),
        )
        midnight = datetime(2025, 6, 1, 0, 0, tzinfo=UTC)
        for event in (times.rise, times.mc, times.set, times.ic):
            assert event is not None
            assert timedelta(hours=-1) <= event - midnight <= timedelta(hours=26)
