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


# Per-planet orbs per Lilly, Christian Astrology I p.107 (the Sun is given as
# 15° there; some editions and later authors carry 17°). Anchors verified in
# the worked moiety example CA I p.127: "the Moity of Saturn his Rayes or Orbs
# is five, and of Venus 4" — Saturn orb 10°, Venus orb 8°. The orb belongs to
# the PLANETS, not to the aspect kind.
LILLY_ORBS: Mapping[Planet, float] = {
    Planet.SATURN: 10.0,
    Planet.JUPITER: 12.0,
    Planet.MARS: 7.5,
    Planet.SUN: 15.0,
    Planet.VENUS: 8.0,
    Planet.MERCURY: 7.0,
    Planet.MOON: 12.5,
}


def lilly_moiety_orb(kind: AspectKind, a: object, b: object) -> float:
    """Lilly moiety orb policy for `compute_aspects(orb_policy=...)`.

    The allowed orb is the sum of the two bodies' half-orbs (moieties),
    independent of the aspect kind (CA I p.127). Endpoints without an orb
    of their own — angles, and bodies outside the Lilly table (outer
    planets, nodes) — contribute a moiety of 0, so such an aspect admits
    only the other endpoint's single moiety. Minor aspects (semisextile /
    quincunx) keep the tight defaults — the moiety doctrine covers
    Ptolemaic aspects.
    """
    if kind in (AspectKind.SEMISEXTILE, AspectKind.QUINCUNX):
        return DEFAULT_ORBS[kind]
    moiety_a = LILLY_ORBS.get(a, 0.0) / 2.0 if isinstance(a, Planet) else 0.0
    moiety_b = LILLY_ORBS.get(b, 0.0) / 2.0 if isinstance(b, Planet) else 0.0
    return moiety_a + moiety_b
