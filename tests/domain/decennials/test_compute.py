"""compute_decennials — Valens decennia (10y9m), sect-conditional sequence."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from astrologica import Planet
from astrologica._internal.domain.decennials.compute import compute_decennials
from astrologica._internal.domain.decennials.types import DECENNIAL_PERIOD_YEARS

pytestmark = pytest.mark.pure


@dataclass
class _FakeChart:
    is_diurnal: bool


def test_decennials_diurnal_starts_with_sun() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=True))
    assert periods[0].ruler is Planet.SUN
    assert periods[0].start_age == 0.0
    assert periods[0].end_age == pytest.approx(10.75)


def test_decennials_nocturnal_starts_with_moon() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=False))
    assert periods[0].ruler is Planet.MOON
    assert periods[0].start_age == 0.0
    assert periods[0].end_age == pytest.approx(10.75)


def test_decennials_diurnal_chaldean_order_from_sun() -> None:
    """Sun -> Venus -> Mercury -> Moon -> Saturn -> Jupiter -> Mars."""
    periods = compute_decennials(_FakeChart(is_diurnal=True), max_age_years=80.0)
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


def test_decennials_all_periods_are_10y9m() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=True), max_age_years=80.0)
    for p in periods:
        assert (p.end_age - p.start_age) == pytest.approx(DECENNIAL_PERIOD_YEARS)


def test_decennials_periods_are_contiguous() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=True))
    for prev, curr in zip(periods[:-1], periods[1:]):
        assert prev.end_age == pytest.approx(curr.start_age)


def test_decennials_full_cycle_is_75y3m() -> None:
    """One full traversal of 7 planets = 7 x 10.75 = 75.25 years."""
    periods = compute_decennials(_FakeChart(is_diurnal=True), max_age_years=80.0)
    assert periods[6].end_age == pytest.approx(75.25)


def test_decennials_repeats_after_first_cycle() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=True), max_age_years=120.0)
    # After 7 periods the cycle repeats — 8th period starts back with Sun.
    assert periods[7].ruler is Planet.SUN


def test_decennials_subperiods_sum_to_major_and_start_with_ruler() -> None:
    periods = compute_decennials(_FakeChart(is_diurnal=True))
    first = periods[0]
    assert len(first.sub_periods) == 7
    # First sub-period is ruled by the major ruler, then walks the sequence.
    assert first.sub_periods[0].ruler is Planet.SUN
    assert first.sub_periods[1].ruler is Planet.VENUS
    # Sub-periods are contiguous and span the whole major period.
    assert first.sub_periods[0].start_age == first.start_age
    assert first.sub_periods[-1].end_age == pytest.approx(first.end_age)
    for prev, curr in zip(first.sub_periods[:-1], first.sub_periods[1:]):
        assert prev.end_age == pytest.approx(curr.start_age)
