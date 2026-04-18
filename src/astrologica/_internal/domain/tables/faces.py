"""Chaldean decans (faces) — 10° subdivisions of each sign, cycling through the 7 planets.

The Chaldean order is: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon (slowest → fastest).
Starting from 0° Aries → Mars, the order cycles through every 10° sign-block.
"""

from __future__ import annotations

from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign

# Chaldean order, slowest → fastest.
_CHALDEAN_ORDER: tuple[Planet, ...] = (
    Planet.SATURN,
    Planet.JUPITER,
    Planet.MARS,
    Planet.SUN,
    Planet.VENUS,
    Planet.MERCURY,
    Planet.MOON,
)

# 0° Aries starts with Mars (index 2 in Chaldean order).
_FIRST_FACE_INDEX = 2


def face_of(sign: Sign, degree_in_sign: float) -> Planet:
    """Return the Chaldean-decan (face) ruler for a position inside a sign."""
    decan_index = int(degree_in_sign // 10)  # 0, 1, or 2
    overall_index = (int(sign) * 3 + decan_index + _FIRST_FACE_INDEX) % 7
    return _CHALDEAN_ORDER[overall_index]


# Table form for introspection: FACES[sign] = (first-decan, second-decan, third-decan).
FACES: dict[Sign, tuple[Planet, Planet, Planet]] = {
    sign: tuple(face_of(sign, d * 10.0 + 1.0) for d in range(3))  # type: ignore[misc]
    for sign in Sign
}
