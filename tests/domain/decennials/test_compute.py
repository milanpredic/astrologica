"""compute_decennials — Valens sect-conditional time-lord sequence."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from astrologica import Planet
from astrologica._internal.domain.decennials.compute import compute_decennials

pytestmark = pytest.mark.pure


@dataclass
class _FakeChart:
    is_diurnal: bool


def test_decennials_diurnal_starts_with_sun() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=True))
    assert periods[0].ruler is Planet.SUN
    assert periods[0].start_age == 0.0
    assert periods[0].end_age == 19.0


def test_decennials_nocturnal_starts_with_moon() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=False))
    assert periods[0].ruler is Planet.MOON
    assert periods[0].start_age == 0.0
    assert periods[0].end_age == 25.0


def test_decennials_diurnal_chaldean_order_from_sun() -> None:
    """Sun → Venus → Mercury → Moon → Saturn → Jupiter → Mars."""
    periods = compute_decennials(_FakeChart(is_diurnal=True), max_age_years=126.0)
    expected = [
        Planet.SUN,
        Planet.VENUS,
        Planet.MERCURY,
        Planet.MOON,
        Planet.SATURN,
        Planet.JUPITER,
        Planet.MARS,
    ]
    assert [p.ruler for p in periods[:7]] == expected


def test_decennials_periods_are_contiguous() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=True))
    for prev, curr in zip(periods[:-1], periods[1:]):
        assert prev.end_age == curr.start_age


def test_decennials_full_cycle_is_126_years() -> None:
    """Sum of one full cycle (Sun=19+Ven=8+Mer=20+Moon=25+Sat=27+Jup=12+Mars=15) = 126."""
    periods = compute_decennials(_FakeChart(is_diurnal=True), max_age_years=126.0)
    assert periods[-1].end_age == 126.0
    assert sum(p.end_age - p.start_age for p in periods) == 126.0


def test_decennials_repeats_after_first_cycle() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=True), max_age_years=200.0)
    # After 7 periods the cycle repeats — 8th period starts back with Sun.
    assert periods[7].ruler is Planet.SUN
