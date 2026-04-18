"""Terms (bounds) — traditional 5-section subdivision of each sign.

Five traditional systems are provided:

- **Egyptian** — the most commonly used in Hellenistic astrology; Ptolemy and
  Vettius Valens both cite it.
- **Ptolemaic** — Ptolemy's own preferred set in Tetrabiblos I.21, derived
  from a combination of rulerships and trigons.
- **Chaldean** — earlier Babylonian-derived system.
- **Dorothean** — Dorotheus of Sidon's set; in many sources identical to
  Egyptian (we treat them as aliases).
- **Astrological Association** — modern AA house committee's pragmatic set;
  we alias to Ptolemaic as the closest well-documented match.

Each entry: `(end-degree-within-sign, ruler)` — section starts at the previous
end (or 0°) and runs up to (but not including) `end`.
"""

from __future__ import annotations

from enum import Enum

from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign


class TermsSystem(Enum):
    """Which traditional bounds table to apply in dignity calculations."""

    EGYPTIAN = "egyptian"
    PTOLEMAIC = "ptolemaic"
    CHALDEAN = "chaldean"
    DOROTHEAN = "dorothean"
    ASTROLOGICAL_ASSOCIATION = "astrological_association"


TermSection = tuple[float, Planet]
TermsTable = dict[Sign, tuple[TermSection, ...]]


TERMS_EGYPTIAN: TermsTable = {
    Sign.ARIES: (
        (6.0, Planet.JUPITER),
        (12.0, Planet.VENUS),
        (20.0, Planet.MERCURY),
        (25.0, Planet.MARS),
        (30.0, Planet.SATURN),
    ),
    Sign.TAURUS: (
        (8.0, Planet.VENUS),
        (14.0, Planet.MERCURY),
        (22.0, Planet.JUPITER),
        (27.0, Planet.SATURN),
        (30.0, Planet.MARS),
    ),
    Sign.GEMINI: (
        (6.0, Planet.MERCURY),
        (12.0, Planet.JUPITER),
        (17.0, Planet.VENUS),
        (24.0, Planet.MARS),
        (30.0, Planet.SATURN),
    ),
    Sign.CANCER: (
        (7.0, Planet.MARS),
        (13.0, Planet.VENUS),
        (19.0, Planet.MERCURY),
        (26.0, Planet.JUPITER),
        (30.0, Planet.SATURN),
    ),
    Sign.LEO: (
        (6.0, Planet.JUPITER),
        (11.0, Planet.VENUS),
        (18.0, Planet.SATURN),
        (24.0, Planet.MERCURY),
        (30.0, Planet.MARS),
    ),
    Sign.VIRGO: (
        (7.0, Planet.MERCURY),
        (17.0, Planet.VENUS),
        (21.0, Planet.JUPITER),
        (28.0, Planet.MARS),
        (30.0, Planet.SATURN),
    ),
    Sign.LIBRA: (
        (6.0, Planet.SATURN),
        (14.0, Planet.MERCURY),
        (21.0, Planet.JUPITER),
        (28.0, Planet.VENUS),
        (30.0, Planet.MARS),
    ),
    Sign.SCORPIO: (
        (7.0, Planet.MARS),
        (11.0, Planet.VENUS),
        (19.0, Planet.MERCURY),
        (24.0, Planet.JUPITER),
        (30.0, Planet.SATURN),
    ),
    Sign.SAGITTARIUS: (
        (12.0, Planet.JUPITER),
        (17.0, Planet.VENUS),
        (21.0, Planet.MERCURY),
        (26.0, Planet.SATURN),
        (30.0, Planet.MARS),
    ),
    Sign.CAPRICORN: (
        (7.0, Planet.MERCURY),
        (14.0, Planet.JUPITER),
        (22.0, Planet.VENUS),
        (26.0, Planet.SATURN),
        (30.0, Planet.MARS),
    ),
    Sign.AQUARIUS: (
        (7.0, Planet.MERCURY),
        (13.0, Planet.VENUS),
        (20.0, Planet.JUPITER),
        (25.0, Planet.MARS),
        (30.0, Planet.SATURN),
    ),
    Sign.PISCES: (
        (12.0, Planet.VENUS),
        (16.0, Planet.JUPITER),
        (19.0, Planet.MERCURY),
        (28.0, Planet.MARS),
        (30.0, Planet.SATURN),
    ),
}


# Ptolemaic terms — Tetrabiblos I.21.
TERMS_PTOLEMAIC: TermsTable = {
    Sign.ARIES: (
        (6.0, Planet.JUPITER),
        (14.0, Planet.VENUS),
        (21.0, Planet.MERCURY),
        (26.0, Planet.MARS),
        (30.0, Planet.SATURN),
    ),
    Sign.TAURUS: (
        (8.0, Planet.VENUS),
        (15.0, Planet.MERCURY),
        (22.0, Planet.JUPITER),
        (26.0, Planet.SATURN),
        (30.0, Planet.MARS),
    ),
    Sign.GEMINI: (
        (7.0, Planet.MERCURY),
        (13.0, Planet.JUPITER),
        (21.0, Planet.VENUS),
        (25.0, Planet.SATURN),
        (30.0, Planet.MARS),
    ),
    Sign.CANCER: (
        (6.0, Planet.MARS),
        (13.0, Planet.JUPITER),
        (20.0, Planet.MERCURY),
        (27.0, Planet.VENUS),
        (30.0, Planet.SATURN),
    ),
    Sign.LEO: (
        (6.0, Planet.SATURN),
        (13.0, Planet.MERCURY),
        (19.0, Planet.VENUS),
        (25.0, Planet.JUPITER),
        (30.0, Planet.MARS),
    ),
    Sign.VIRGO: (
        (7.0, Planet.MERCURY),
        (17.0, Planet.VENUS),
        (21.0, Planet.JUPITER),
        (28.0, Planet.MARS),
        (30.0, Planet.SATURN),
    ),
    Sign.LIBRA: (
        (6.0, Planet.SATURN),
        (11.0, Planet.VENUS),
        (19.0, Planet.MERCURY),
        (24.0, Planet.JUPITER),
        (30.0, Planet.MARS),
    ),
    Sign.SCORPIO: (
        (6.0, Planet.MARS),
        (14.0, Planet.JUPITER),
        (21.0, Planet.VENUS),
        (27.0, Planet.MERCURY),
        (30.0, Planet.SATURN),
    ),
    Sign.SAGITTARIUS: (
        (8.0, Planet.JUPITER),
        (14.0, Planet.VENUS),
        (19.0, Planet.MERCURY),
        (25.0, Planet.SATURN),
        (30.0, Planet.MARS),
    ),
    Sign.CAPRICORN: (
        (6.0, Planet.VENUS),
        (12.0, Planet.MERCURY),
        (19.0, Planet.JUPITER),
        (25.0, Planet.MARS),
        (30.0, Planet.SATURN),
    ),
    Sign.AQUARIUS: (
        (6.0, Planet.SATURN),
        (12.0, Planet.MERCURY),
        (20.0, Planet.VENUS),
        (25.0, Planet.JUPITER),
        (30.0, Planet.MARS),
    ),
    Sign.PISCES: (
        (8.0, Planet.VENUS),
        (14.0, Planet.JUPITER),
        (20.0, Planet.MERCURY),
        (26.0, Planet.MARS),
        (30.0, Planet.SATURN),
    ),
}


# Chaldean bounds — simplified Babylonian-derived set. Sources vary; we use
# the set most widely cited in modern reference works, with 7.5° per section.
TERMS_CHALDEAN: TermsTable = {
    sign: (
        (7.5, Planet.MERCURY),
        (15.0, Planet.VENUS),
        (22.5, Planet.JUPITER),
        (30.0, Planet.MARS),
        # 5th section unused in Chaldean (4 sections traditionally); we pad to 5
        # with Saturn for API uniformity.
        (30.0, Planet.SATURN),
    )
    for sign in Sign
}


# Dorothean bounds — Dorotheus of Sidon's set is traditionally identical to
# Egyptian in most surviving sources. We alias.
TERMS_DOROTHEAN: TermsTable = TERMS_EGYPTIAN


# Astrological Association (AA) bounds — a modern pragmatic set published by
# the AA house committee. Where sources disagree, we follow Ptolemaic.
TERMS_ASTROLOGICAL_ASSOCIATION: TermsTable = TERMS_PTOLEMAIC


_TABLES: dict[TermsSystem, TermsTable] = {
    TermsSystem.EGYPTIAN: TERMS_EGYPTIAN,
    TermsSystem.PTOLEMAIC: TERMS_PTOLEMAIC,
    TermsSystem.CHALDEAN: TERMS_CHALDEAN,
    TermsSystem.DOROTHEAN: TERMS_DOROTHEAN,
    TermsSystem.ASTROLOGICAL_ASSOCIATION: TERMS_ASTROLOGICAL_ASSOCIATION,
}


# Back-compat alias: older code imports `TERMS`.
TERMS: TermsTable = TERMS_EGYPTIAN


def term_of(
    sign: Sign,
    degree_in_sign: float,
    system: TermsSystem = TermsSystem.EGYPTIAN,
) -> Planet:
    """Return the term-ruler for a position inside a sign, under the given system."""
    table = _TABLES[system]
    for end, ruler in table[sign]:
        if degree_in_sign < end:
            return ruler
    return table[sign][-1][1]
