"""PlanetPosition — a planet's state at a specific moment."""

from __future__ import annotations

from dataclasses import dataclass, field

from astrologica._internal.domain.dignity.dignity import Dignity
from astrologica._internal.domain.measures.ecliptic import EclipticPosition
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign


@dataclass(frozen=True, slots=True)
class PlanetPosition:
    """A planet placed in a chart — its identity + computed state + dignities."""

    planet: Planet
    position: EclipticPosition
    dignities: frozenset[Dignity] = field(default_factory=frozenset)

    @property
    def sign(self) -> Sign:
        return Sign.of(self.position.longitude)

    @property
    def degree_in_sign(self) -> float:
        return Sign.degree_in(self.position.longitude)

    @property
    def is_retrograde(self) -> bool:
        return self.position.speed.is_retrograde

    @property
    def longitude(self) -> float:
        return float(self.position.longitude)
