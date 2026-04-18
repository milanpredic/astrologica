"""HouseCusp — longitude of a house cusp at a specific moment."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.house.house import House
from astrologica._internal.domain.measures.angle import Longitude
from astrologica._internal.domain.sign import Sign


@dataclass(frozen=True, slots=True)
class HouseCusp:
    """The cusp of one of the twelve houses at a given moment, for a given place."""

    house: House
    cusp: Longitude

    @property
    def sign(self) -> Sign:
        return Sign.of(self.cusp)

    @property
    def degree_in_sign(self) -> float:
        return Sign.degree_in(self.cusp)
