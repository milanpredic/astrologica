"""Diurnal / nocturnal determination."""

from __future__ import annotations

import pytest

from astrologica.diurnal import compute_is_diurnal

pytestmark = pytest.mark.pure


class TestComputeIsDiurnal:
    def test_sun_above_horizon(self) -> None:
        # ASC at 0°; Sun at 270° → (270-0) mod 360 = 270 ≥ 180 → 10th house area → above horizon.
        assert compute_is_diurnal(sun_longitude=270.0, ascendant=0.0) is True

    def test_sun_below_horizon(self) -> None:
        # Sun at 90° with ASC at 0° → (90-0) mod 360 = 90 < 180 → 4th house area → below horizon.
        assert compute_is_diurnal(sun_longitude=90.0, ascendant=0.0) is False

    def test_sun_at_ascendant_is_just_rising_still_night(self) -> None:
        # Exactly on the ASC -> 1st-house cusp — traditionally considered nocturnal.
        assert compute_is_diurnal(sun_longitude=45.0, ascendant=45.0) is False

    def test_sun_opposite_ascendant_at_descendant(self) -> None:
        # Exactly setting = on the DESC (7th cusp) — traditionally considered diurnal.
        assert compute_is_diurnal(sun_longitude=225.0, ascendant=45.0) is True

    def test_wraps_across_zero(self) -> None:
        # ASC at 350°, Sun at 170° — lon-asc = -180 mod 360 = 180, so diurnal.
        assert compute_is_diurnal(sun_longitude=170.0, ascendant=350.0) is True
