"""compute_lots — the seven Hellenistic lots.

Lot formulae (day / night). Each formula has the form ASC + X - Y, where X and Y
swap when switching between diurnal and nocturnal charts.

| Lot        | Day                   | Night                 |
|------------|-----------------------|-----------------------|
| Fortune    | ASC + Moon - Sun      | ASC + Sun  - Moon     |
| Spirit     | ASC + Sun  - Moon     | ASC + Moon - Sun      |
| Eros       | ASC + Venus - Spirit  | ASC + Spirit - Venus  |
| Necessity  | ASC + Fortune - Mercury | ASC + Mercury - Fortune |
| Courage    | ASC + Fortune - Mars  | ASC + Mars - Fortune  |
| Victory    | ASC + Jupiter - Spirit | ASC + Spirit - Jupiter |
| Nemesis    | ASC + Fortune - Saturn | ASC + Saturn - Fortune |
"""

from __future__ import annotations

from collections.abc import Mapping

from astrologica._internal.domain.lot.lot import Lot
from astrologica._internal.domain.lot.position import LotPosition
from astrologica._internal.domain.measures.angle import Longitude, normalize_longitude
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition


def _lon(positions: Mapping[Planet, PlanetPosition], planet: Planet) -> float:
    return positions[planet].longitude


def _fortune(positions: Mapping[Planet, PlanetPosition], asc: float, is_diurnal: bool) -> float:
    if is_diurnal:
        return normalize_longitude(asc + _lon(positions, Planet.MOON) - _lon(positions, Planet.SUN))
    return normalize_longitude(asc + _lon(positions, Planet.SUN) - _lon(positions, Planet.MOON))


def _spirit(positions: Mapping[Planet, PlanetPosition], asc: float, is_diurnal: bool) -> float:
    if is_diurnal:
        return normalize_longitude(asc + _lon(positions, Planet.SUN) - _lon(positions, Planet.MOON))
    return normalize_longitude(asc + _lon(positions, Planet.MOON) - _lon(positions, Planet.SUN))


def compute_lots(
    positions: Mapping[Planet, PlanetPosition],
    ascendant: float,
    is_diurnal: bool,
) -> Mapping[Lot, LotPosition]:
    """Return the seven Hellenistic lots, keyed by Lot enum."""
    asc = normalize_longitude(ascendant)
    fortune = _fortune(positions, asc, is_diurnal)
    spirit = _spirit(positions, asc, is_diurnal)

    def make(day_a: float, day_b: float, night_a: float, night_b: float) -> float:
        if is_diurnal:
            return normalize_longitude(asc + day_a - day_b)
        return normalize_longitude(asc + night_a - night_b)

    mercury = _lon(positions, Planet.MERCURY)
    venus = _lon(positions, Planet.VENUS)
    mars = _lon(positions, Planet.MARS)
    jupiter = _lon(positions, Planet.JUPITER)
    saturn = _lon(positions, Planet.SATURN)

    lons: dict[Lot, float] = {
        Lot.FORTUNE: fortune,
        Lot.SPIRIT: spirit,
        Lot.EROS: make(venus, spirit, spirit, venus),
        Lot.NECESSITY: make(fortune, mercury, mercury, fortune),
        Lot.COURAGE: make(fortune, mars, mars, fortune),
        Lot.VICTORY: make(jupiter, spirit, spirit, jupiter),
        Lot.NEMESIS: make(fortune, saturn, saturn, fortune),
    }

    return {lot: LotPosition(lot=lot, longitude=Longitude(lon)) for lot, lon in lons.items()}
