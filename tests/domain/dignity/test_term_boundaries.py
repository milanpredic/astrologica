"""term_boundaries — enumerate term ruler-spans across the zodiac."""

from __future__ import annotations

import pytest

from astrologica import Planet, Sign

pytestmark = pytest.mark.pure


def test_term_boundaries_egyptian_returns_60_entries() -> None:
    from astrologica._internal.domain.tables.terms import TermsSystem, term_boundaries

    boundaries = term_boundaries(TermsSystem.EGYPTIAN)
    assert len(boundaries) == 60


def test_term_boundaries_sorted_by_start_longitude() -> None:
    from astrologica._internal.domain.tables.terms import TermsSystem, term_boundaries

    boundaries = term_boundaries(TermsSystem.EGYPTIAN)
    starts = [b.start_longitude for b in boundaries]
    assert starts == sorted(starts)


def test_term_boundaries_first_entry_is_aries_jupiter_0_to_6() -> None:
    from astrologica._internal.domain.tables.terms import TermsSystem, term_boundaries

    boundaries = term_boundaries(TermsSystem.EGYPTIAN)
    first = boundaries[0]
    assert first.start_longitude == 0.0
    assert first.end_longitude == 6.0
    assert first.sign is Sign.ARIES
    assert first.ruler is Planet.JUPITER


def test_term_boundaries_last_entry_ends_at_360() -> None:
    from astrologica._internal.domain.tables.terms import TermsSystem, term_boundaries

    boundaries = term_boundaries(TermsSystem.EGYPTIAN)
    assert boundaries[-1].end_longitude == 360.0


def test_term_boundaries_contiguous_no_gaps() -> None:
    from astrologica._internal.domain.tables.terms import TermsSystem, term_boundaries

    boundaries = term_boundaries(TermsSystem.EGYPTIAN)
    for prev, curr in zip(boundaries[:-1], boundaries[1:]):
        assert prev.end_longitude == curr.start_longitude


def test_term_boundaries_chaldean_drops_padded_saturn_row() -> None:
    from astrologica._internal.domain.tables.terms import TermsSystem, term_boundaries

    boundaries = term_boundaries(TermsSystem.CHALDEAN)
    # Chaldean: 4 sections per sign × 12 signs = 48 (the padded 5th Saturn span is dropped).
    assert len(boundaries) == 48
