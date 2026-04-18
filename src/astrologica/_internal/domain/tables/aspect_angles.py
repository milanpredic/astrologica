"""Ptolemaic aspect angles + default orb policy."""

from __future__ import annotations

from collections.abc import Mapping

from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.planet.planet import Planet

# Default orbs, in degrees, per aspect kind (classical "moiety" approach simplified).
DEFAULT_ORBS: Mapping[AspectKind, float] = {
    AspectKind.CONJUNCTION: 8.0,
    AspectKind.OPPOSITION: 8.0,
    AspectKind.TRINE: 7.0,
    AspectKind.SQUARE: 6.0,
    AspectKind.SEXTILE: 4.0,
    # Semisextile / quincunx are weak aspects — tight default orbs.
    AspectKind.SEMISEXTILE: 2.0,
    AspectKind.QUINCUNX: 2.0,
}

# Wider orbs for the luminaries, classical tradition.
LUMINARY_ORB_BONUS: Mapping[Planet, float] = {
    Planet.SUN: 4.0,
    Planet.MOON: 4.0,
}


def default_orb(kind: AspectKind, a: Planet, b: Planet) -> float:
    """Default orb for `kind` between planets `a` and `b`.

    Uses the aspect's base orb plus a luminary bonus (0, 2, or 4) depending on how
    many luminaries are involved — a simple, permissive policy acceptable for natal
    aspects. Callers can override by passing their own orb policy.
    """
    base = DEFAULT_ORBS[kind]
    bonus = (LUMINARY_ORB_BONUS.get(a, 0.0) + LUMINARY_ORB_BONUS.get(b, 0.0)) / 2.0
    return base + bonus
