"""Oriental vs occidental classification of a planet relative to the Sun.

Geometric definition: a planet is ORIENTAL of the Sun if it rises before
the Sun — i.e. its ecliptic longitude is BEHIND the Sun's (smaller, with
0..180° tolerance accounting for wraparound). OCCIDENTAL is the symmetric
case (longitude ahead of the Sun, 0..180° tolerance).

The Sun and Moon are returned as NEUTRAL — orientality is meaningful only
for the five non-luminary classical planets.

This function returns the geometric state. Whether ORIENTAL or OCCIDENTAL
is "stronger" is a sect-conditional editorial decision; callers (e.g. the
Almuten modifier scheme) apply that interpretation themselves.
"""

from __future__ import annotations

from collections.abc import Mapping

from astrologica._internal.domain.orientality.types import Orientality
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition

__all__ = ["Orientality", "planet_orientality"]


def planet_orientality(
    planet: Planet,
    planets: Mapping[Planet, PlanetPosition],
) -> Orientality:
    """Classify `planet` as ORIENTAL, OCCIDENTAL, or NEUTRAL of the Sun.

    `planets` must contain at least Sun and the target planet.
    """
    if planet.is_luminary:
        return Orientality.NEUTRAL

    sun_lon = float(planets[Planet.SUN].position.longitude)
    pl_lon = float(planets[planet].position.longitude)

    diff = ((pl_lon - sun_lon) + 180.0) % 360.0 - 180.0

    if diff > 0:
        return Orientality.OCCIDENTAL
    if diff < 0:
        return Orientality.ORIENTAL
    return Orientality.NEUTRAL
