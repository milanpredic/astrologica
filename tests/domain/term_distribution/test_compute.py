"""compute_term_distribution — Naibod-directed Ascendant through term boundaries."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from astrologica import Planet, Sign, TermsSystem
from astrologica._internal.domain.term_distribution.compute import (
    _NAIBOD_DEGREES_PER_YEAR,
    compute_term_distribution,
)

pytestmark = pytest.mark.pure


@dataclass
class _FakeChart:
    ascendant: float


def test_term_distribution_first_period_starts_at_age_zero() -> None:
    periods = compute_term_distribution(_FakeChart(ascendant=0.0), max_age_years=82.0)
    assert periods[0].start_age == 0.0


def test_term_distribution_periods_are_contiguous() -> None:
    periods = compute_term_distribution(_FakeChart(ascendant=12.5), max_age_years=82.0)
    for prev, curr in zip(periods[:-1], periods[1:]):
        assert prev.end_age == curr.start_age


def test_term_distribution_last_period_ends_at_max_age() -> None:
    periods = compute_term_distribution(_FakeChart(ascendant=0.0), max_age_years=82.0)
    assert periods[-1].end_age == pytest.approx(82.0)


def test_term_distribution_first_ruler_at_aries_zero_is_jupiter() -> None:
    """Egyptian terms: Aries 0-6 = Jupiter."""
    periods = compute_term_distribution(_FakeChart(ascendant=0.0))
    assert periods[0].ruler is Planet.JUPITER
    assert periods[0].sign is Sign.ARIES


def test_term_distribution_first_period_length_matches_naibod_rate() -> None:
    """Asc at 0° Aries: first term ends at 6° (Jupiter→Venus). Span = 6°,
    duration = 6 / 0.98565 ≈ 6.087 years."""
    periods = compute_term_distribution(_FakeChart(ascendant=0.0))
    expected = 6.0 / _NAIBOD_DEGREES_PER_YEAR
    assert periods[0].end_age == pytest.approx(expected)


def test_term_distribution_handles_zodiac_wrap() -> None:
    """Asc near end of Pisces: first period crosses 360° boundary into Aries."""
    periods = compute_term_distribution(_FakeChart(ascendant=358.0), max_age_years=82.0)
    # First period: Pisces 28°-360° (Saturn term), span 2°.
    assert periods[0].sign is Sign.PISCES
    assert periods[0].ruler is Planet.SATURN
    # Second period: Aries 0°-6° (Jupiter term).
    assert periods[1].sign is Sign.ARIES
    assert periods[1].ruler is Planet.JUPITER


def test_term_distribution_alternate_terms_system() -> None:
    """Egyptian and Ptolemaic Aries 0°: both place Jupiter as first term ruler."""
    egy = compute_term_distribution(_FakeChart(ascendant=0.0), terms_system=TermsSystem.EGYPTIAN)
    pto = compute_term_distribution(_FakeChart(ascendant=0.0), terms_system=TermsSystem.PTOLEMAIC)
    assert egy[0].ruler is Planet.JUPITER
    assert pto[0].ruler is Planet.JUPITER
