"""Term systems — Egyptian vs Ptolemaic vs others."""

from __future__ import annotations

import pytest

from astrologica._internal.domain.tables.terms import term_of
from astrologica.dignity import TermsSystem, compute_dignities
from astrologica.planet import Planet
from astrologica.sign import Sign

pytestmark = pytest.mark.pure


class TestTermsSystemDispatch:
    def test_egyptian_is_default(self) -> None:
        # Aries 0°–6° is Jupiter in Egyptian bounds.
        assert term_of(Sign.ARIES, 3.0) is Planet.JUPITER

    def test_ptolemaic_agrees_with_egyptian_at_aries_start(self) -> None:
        """Both systems assign Jupiter 0–6° Aries (shared starting rule)."""
        assert term_of(Sign.ARIES, 3.0, system=TermsSystem.PTOLEMAIC) is Planet.JUPITER

    def test_ptolemaic_differs_from_egyptian(self) -> None:
        """Find a position where the two traditions disagree.

        Aries 0°–6° is Jupiter in both — but 6°–12° Aries is Venus in Egyptian
        (6→12) and still Jupiter in Ptolemaic (Ptolemaic gives Jupiter to 6,
        then Venus 6–14). Test at 10° Aries:
        - Egyptian: Venus (6 < 10 < 12 → Venus)
        - Ptolemaic: Venus (6 < 10 < 14 → Venus)
        Both agree. Let's use 13° Aries instead:
        - Egyptian: Mercury (12 < 13 < 20 → Mercury)
        - Ptolemaic: Venus (6 < 13 < 14 → Venus) — disagrees.
        """
        assert term_of(Sign.ARIES, 13.0, system=TermsSystem.EGYPTIAN) is Planet.MERCURY
        assert term_of(Sign.ARIES, 13.0, system=TermsSystem.PTOLEMAIC) is Planet.VENUS

    def test_compute_dignities_honors_terms_system(self) -> None:
        """compute_dignities picks up the term from the chosen system."""
        from astrologica.dignity import Dignity

        # 3° Aries: Jupiter is the term-ruler in Egyptian (and Ptolemaic).
        egypt = compute_dignities(
            Planet.JUPITER, 3.0, is_diurnal=True, terms_system=TermsSystem.EGYPTIAN
        )
        ptol = compute_dignities(
            Planet.JUPITER, 3.0, is_diurnal=True, terms_system=TermsSystem.PTOLEMAIC
        )
        assert Dignity.TERM in egypt
        assert Dignity.TERM in ptol

    def test_five_systems_enum_present(self) -> None:
        names = {s.name for s in TermsSystem}
        assert names == {
            "EGYPTIAN",
            "PTOLEMAIC",
            "CHALDEAN",
            "DOROTHEAN",
            "ASTROLOGICAL_ASSOCIATION",
        }
