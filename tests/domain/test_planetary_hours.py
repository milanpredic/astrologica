"""Planetary hours — Chaldean-order hours for a day at a place."""

from __future__ import annotations

from datetime import date

import pytest

from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.planetary_hours import compute_planetary_hours
from astrologica.swisseph import SwissEphemerisAdapter

pytestmark = pytest.mark.infrastructure


class TestPlanetaryHours:
    def test_twenty_four_hours_returned(self) -> None:
        # 2025-06-01 Greenwich
        hours = compute_planetary_hours(
            date(2025, 6, 1),
            Place(latitude=0.0, longitude=0.0),
            ephemeris=SwissEphemerisAdapter(),
        )
        assert len(hours) == 24

    def test_first_day_hour_matches_weekday_ruler(self) -> None:
        # 2025-06-01 was a Sunday → first hour should be Sun.
        hours = compute_planetary_hours(
            date(2025, 6, 1),
            Place(latitude=0.0, longitude=0.0),
            ephemeris=SwissEphemerisAdapter(),
        )
        assert hours[0].ruler is Planet.SUN
        assert hours[0].is_daytime is True

    def test_twelve_day_then_twelve_night(self) -> None:
        hours = compute_planetary_hours(
            date(2025, 6, 1),
            Place(latitude=0.0, longitude=0.0),
            ephemeris=SwissEphemerisAdapter(),
        )
        day_count = sum(1 for h in hours if h.is_daytime)
        night_count = sum(1 for h in hours if not h.is_daytime)
        assert day_count == 12
        assert night_count == 12

    def test_hours_tile_the_day(self) -> None:
        hours = compute_planetary_hours(
            date(2025, 6, 1),
            Place(latitude=0.0, longitude=0.0),
            ephemeris=SwissEphemerisAdapter(),
        )
        # Each hour ends where the next begins (no gaps, no overlaps).
        for a, b in zip(hours, hours[1:], strict=False):
            assert a.end == b.start

    def test_chaldean_cycle_after_twenty_four_hours(self) -> None:
        """Hour 25 (if there was one) would be ruled by the same planet as hour 1.

        Since 24 = 3×7 + 3, the hour that comes right after the last night hour
        cycles back with a 3-step offset — which is why the weekday ruler
        advances. We verify the Chaldean step-of-one within the day.
        """
        chaldean = [
            Planet.SATURN,
            Planet.JUPITER,
            Planet.MARS,
            Planet.SUN,
            Planet.VENUS,
            Planet.MERCURY,
            Planet.MOON,
        ]
        hours = compute_planetary_hours(
            date(2025, 6, 1),
            Place(latitude=0.0, longitude=0.0),
            ephemeris=SwissEphemerisAdapter(),
        )
        for a, b in zip(hours, hours[1:], strict=False):
            ia = chaldean.index(a.ruler)
            ib = chaldean.index(b.ruler)
            assert (ib - ia) % 7 == 1
