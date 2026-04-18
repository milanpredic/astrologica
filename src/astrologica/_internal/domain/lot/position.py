"""LotPosition — where a Hellenistic lot sits in a chart."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.lot.lot import Lot
from astrologica._internal.domain.measures.angle import Longitude
from astrologica._internal.domain.sign import Sign


@dataclass(frozen=True, slots=True)
class LotPosition:
    """Position of a lot (e.g. Lot of Fortune) at a given chart."""

    lot: Lot
    longitude: Longitude

    @property
    def sign(self) -> Sign:
        return Sign.of(self.longitude)

    @property
    def degree_in_sign(self) -> float:
        return Sign.degree_in(self.longitude)
