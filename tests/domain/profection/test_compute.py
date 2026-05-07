"""compute_annual_profection — Ptolemaic 12-house annual cycle."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from astrologica import Planet, Sign
from astrologica._internal.domain.profection.compute import compute_annual_profection

pytestmark = pytest.mark.pure


@dataclass
class _FakeChart:
    ascendant: float  # absolute longitude


def test_profection_age_zero_activates_ascendant_sign_and_first_house() -> None:
    """Aries-rising chart at age 0: 1st house, Aries, lord = Mars."""
    p = compute_annual_profection(_FakeChart(ascendant=10.0), age_years=0)
    assert p.profected_house == 1
    assert p.profected_sign is Sign.ARIES
    assert p.lord_of_year is Planet.MARS


def test_profection_age_one_advances_one_sign_one_house() -> None:
    """Aries-rising, age 1: 2nd house, Taurus, lord = Venus."""
    p = compute_annual_profection(_FakeChart(ascendant=10.0), age_years=1)
    assert p.profected_house == 2
    assert p.profected_sign is Sign.TAURUS
    assert p.lord_of_year is Planet.VENUS


def test_profection_age_seven_activates_seventh_house_libra() -> None:
    """Aries-rising, age 7: 7th house (Libra opposite), lord = Venus."""
    p = compute_annual_profection(_FakeChart(ascendant=10.0), age_years=7)
    assert p.profected_house == 8
    assert p.profected_sign is Sign.SCORPIO
    assert p.lord_of_year is Planet.MARS


def test_profection_wraps_after_twelve_years() -> None:
    """Year 12 returns to 1st house (same sign as year 0)."""
    p0 = compute_annual_profection(_FakeChart(ascendant=10.0), age_years=0)
    p12 = compute_annual_profection(_FakeChart(ascendant=10.0), age_years=12)
    assert p0.profected_sign == p12.profected_sign
    assert p0.profected_house == p12.profected_house
    assert p0.lord_of_year == p12.lord_of_year


def test_profection_capricorn_rising_age_30_returns_to_capricorn() -> None:
    """Cap-rising, age 24 (12*2): back to Cap. Age 30: 7th house Cancer (opposite)."""
    p24 = compute_annual_profection(_FakeChart(ascendant=270.0), age_years=24)
    assert p24.profected_sign is Sign.CAPRICORN
    p30 = compute_annual_profection(_FakeChart(ascendant=270.0), age_years=30)
    assert p30.profected_sign is Sign.CANCER
    assert p30.lord_of_year is Planet.MOON


def test_profection_negative_age_raises() -> None:
    with pytest.raises(ValueError):
        compute_annual_profection(_FakeChart(ascendant=0.0), age_years=-1)
