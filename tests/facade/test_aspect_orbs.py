"""Promoted orb tables and helper."""

from __future__ import annotations

import pytest

from astrologica import AspectKind, Planet

pytestmark = pytest.mark.pure


def test_default_orbs_match_classical_moieties() -> None:
    from astrologica.aspect import DEFAULT_ORBS

    assert DEFAULT_ORBS[AspectKind.CONJUNCTION] == 8.0
    assert DEFAULT_ORBS[AspectKind.OPPOSITION] == 8.0
    assert DEFAULT_ORBS[AspectKind.TRINE] == 7.0
    assert DEFAULT_ORBS[AspectKind.SQUARE] == 6.0
    assert DEFAULT_ORBS[AspectKind.SEXTILE] == 4.0
    assert DEFAULT_ORBS[AspectKind.SEMISEXTILE] == 2.0
    assert DEFAULT_ORBS[AspectKind.QUINCUNX] == 2.0


def test_luminary_orb_bonus_for_sun_and_moon() -> None:
    from astrologica.aspect import LUMINARY_ORB_BONUS

    assert LUMINARY_ORB_BONUS[Planet.SUN] == 4.0
    assert LUMINARY_ORB_BONUS[Planet.MOON] == 4.0


def test_default_orb_helper_adds_luminary_bonus() -> None:
    from astrologica.aspect import default_orb

    base = default_orb(AspectKind.SQUARE, Planet.MARS, Planet.JUPITER)
    luminary = default_orb(AspectKind.SQUARE, Planet.SUN, Planet.JUPITER)
    assert luminary > base
