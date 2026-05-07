"""Public-facade smoke test for astrologica.terms."""

from __future__ import annotations

import pytest

from astrologica import Planet, Sign

pytestmark = pytest.mark.pure


def test_terms_facade_exports_all_tables() -> None:
    from astrologica.terms import (
        TERMS_EGYPTIAN,
        TermBoundary,
        TermsSystem,
        term_boundaries,
        term_of,
    )

    assert term_of(Sign.ARIES, 0.0, TermsSystem.EGYPTIAN) is Planet.JUPITER
    boundaries = term_boundaries(TermsSystem.EGYPTIAN)
    assert isinstance(boundaries[0], TermBoundary)
    assert TERMS_EGYPTIAN[Sign.ARIES][0] == (6.0, Planet.JUPITER)


def test_terms_system_still_importable_from_dignity_for_back_compat() -> None:
    from astrologica.dignity import TermsSystem  # noqa: F401
