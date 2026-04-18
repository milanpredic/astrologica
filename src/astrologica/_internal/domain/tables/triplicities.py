"""Triplicity rulers — Dorothean scheme (day / night / participating) by element."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Element, Sign


@dataclass(frozen=True, slots=True)
class TriplicityRulers:
    day: Planet
    night: Planet
    participating: Planet


# Dorothean triplicity rulers by element.
TRIPLICITY_BY_ELEMENT: dict[Element, TriplicityRulers] = {
    Element.FIRE: TriplicityRulers(
        day=Planet.SUN, night=Planet.JUPITER, participating=Planet.SATURN
    ),
    Element.EARTH: TriplicityRulers(day=Planet.VENUS, night=Planet.MOON, participating=Planet.MARS),
    Element.AIR: TriplicityRulers(
        day=Planet.SATURN, night=Planet.MERCURY, participating=Planet.JUPITER
    ),
    Element.WATER: TriplicityRulers(day=Planet.VENUS, night=Planet.MARS, participating=Planet.MOON),
}


def triplicity_of(sign: Sign) -> TriplicityRulers:
    return TRIPLICITY_BY_ELEMENT[sign.element]
