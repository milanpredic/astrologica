"""Rising times of the 12 signs at a geographic latitude."""

from __future__ import annotations

import pytest

from astrologica.rising_times import compute_rising_times
from astrologica.sign import Sign

pytestmark = pytest.mark.pure


class TestRisingTimes:
    def test_at_equator_rising_times_sum_to_360(self) -> None:
        """At the equator, the 12 rising times sum to 360° exactly (one sidereal day).

        Individual sign rising times aren't exactly 30° even at the equator — the
        ecliptic's tilt against the celestial equator distorts each sign's RA
        projection. Signs near the equinoxes take less RA to rise (~27.9°) and
        signs near the solstices take more (~32.1°), but the sum is 360°.
        """
        times = compute_rising_times(latitude_deg=0.0)
        assert sum(times.values()) == pytest.approx(360.0, abs=0.01)
        # Each sign rises within a few degrees of 30° at the equator.
        for sign, t in times.items():
            assert 27.0 < t < 33.0, f"{sign.name}: {t}° out of expected range"

    def test_sum_is_360_at_temperate_latitude(self) -> None:
        times = compute_rising_times(latitude_deg=40.0)
        total = sum(t for t in times.values())
        assert total == pytest.approx(360.0, abs=0.1)

    def test_long_ascension_signs_at_northern_latitude(self) -> None:
        """At 40°N, long-ascension signs (Cancer → Sagittarius) take > 30° to rise."""
        times = compute_rising_times(latitude_deg=40.0)
        for sign in (Sign.CANCER, Sign.LEO, Sign.VIRGO, Sign.LIBRA, Sign.SCORPIO, Sign.SAGITTARIUS):
            assert times[sign] > 30.0, f"{sign.name} should be long-ascension at 40°N"

    def test_short_ascension_signs_at_northern_latitude(self) -> None:
        """At 40°N, short-ascension signs (Capricorn → Gemini) take < 30° to rise."""
        times = compute_rising_times(latitude_deg=40.0)
        for sign in (
            Sign.CAPRICORN,
            Sign.AQUARIUS,
            Sign.PISCES,
            Sign.ARIES,
            Sign.TAURUS,
            Sign.GEMINI,
        ):
            assert times[sign] < 30.0, f"{sign.name} should be short-ascension at 40°N"
