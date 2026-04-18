"""Essential-dignity tables keyed by Sign.

Classic Ptolemaic-Hellenistic rulership scheme (seven planets, no outer rulers).
"""

from __future__ import annotations

from collections.abc import Mapping

from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign

DOMICILE: Mapping[Sign, Planet] = {
    Sign.ARIES: Planet.MARS,
    Sign.TAURUS: Planet.VENUS,
    Sign.GEMINI: Planet.MERCURY,
    Sign.CANCER: Planet.MOON,
    Sign.LEO: Planet.SUN,
    Sign.VIRGO: Planet.MERCURY,
    Sign.LIBRA: Planet.VENUS,
    Sign.SCORPIO: Planet.MARS,
    Sign.SAGITTARIUS: Planet.JUPITER,
    Sign.CAPRICORN: Planet.SATURN,
    Sign.AQUARIUS: Planet.SATURN,
    Sign.PISCES: Planet.JUPITER,
}

EXALTATION: Mapping[Sign, Planet] = {
    Sign.ARIES: Planet.SUN,
    Sign.TAURUS: Planet.MOON,
    Sign.CANCER: Planet.JUPITER,
    Sign.VIRGO: Planet.MERCURY,
    Sign.LIBRA: Planet.SATURN,
    Sign.CAPRICORN: Planet.MARS,
    Sign.PISCES: Planet.VENUS,
}

# DETRIMENT and FALL are derived: opposite sign of domicile/exaltation respectively.
DETRIMENT: Mapping[Sign, Planet] = {
    Sign((int(sign) + 6) % 12): planet for sign, planet in DOMICILE.items()
}

FALL: Mapping[Sign, Planet] = {
    Sign((int(sign) + 6) % 12): planet for sign, planet in EXALTATION.items()
}
