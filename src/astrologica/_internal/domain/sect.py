"""Planetary sect conditions — in-sect, halb, hayz.

Doctrine (Dösser, *The Art of Horary Astrology* p.201; standard medieval
usage): **halb** = a planet of the correct sect in the correct hemisphere —
a diurnal planet above the horizon by day or below it by night; a nocturnal
planet above the horizon by night or below it by day. **Hayz** = halb plus
gender agreement between planet and sign (a masculine planet in a masculine
sign, a feminine planet in a feminine sign).

Sect membership: diurnal — Sun, Jupiter, Saturn; nocturnal — Moon, Venus,
Mars. Mercury takes its sect (and gender) from orientality: oriental of the
Sun → diurnal/masculine, occidental → nocturnal/feminine (Ptolemy I.7); when
neutral (cazimi-close), it follows the sect of the chart.

Hemisphere placement uses the ecliptic approximation (a body whose longitude
has already risen past the Ascendant degree is above the horizon) — the
method of the traditional sources themselves; planetary latitude is ignored.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from astrologica._internal.domain.orientality.compute import planet_orientality
from astrologica._internal.domain.orientality.types import Orientality
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition

__all__ = ["PlanetSect", "SectStatus", "compute_sect_statuses"]


class PlanetSect(Enum):
    DIURNAL = "diurnal"
    NOCTURNAL = "nocturnal"


_DIURNAL_PLANETS = frozenset({Planet.SUN, Planet.JUPITER, Planet.SATURN})
_NOCTURNAL_PLANETS = frozenset({Planet.MOON, Planet.VENUS, Planet.MARS})

# Gender: masculine — Sun, Mars, Jupiter, Saturn; feminine — Moon, Venus;
# Mercury by orientality (masculine when oriental, feminine when occidental).
_MASCULINE_PLANETS = frozenset({Planet.SUN, Planet.MARS, Planet.JUPITER, Planet.SATURN})
_FEMININE_PLANETS = frozenset({Planet.MOON, Planet.VENUS})


@dataclass(frozen=True)
class SectStatus:
    """Sect condition of one planet within a chart."""

    planet: Planet
    planet_sect: PlanetSect
    in_sect: bool
    above_horizon: bool
    in_halb: bool
    in_hayz: bool
    masculine: bool
    sign_gender_match: bool


def _is_above_horizon(longitude: float, ascendant: float) -> bool:
    """Ecliptic approximation: degrees that already rose are above the horizon."""
    return ((ascendant - longitude) % 360.0) < 180.0


def _sign_is_masculine(longitude: float) -> bool:
    """Odd signs (Aries, Gemini, …) are masculine; even are feminine."""
    return int(longitude // 30.0) % 2 == 0


def _planet_sect(
    planet: Planet,
    positions: Mapping[Planet, PlanetPosition],
    is_diurnal_chart: bool,
) -> PlanetSect:
    if planet in _DIURNAL_PLANETS:
        return PlanetSect.DIURNAL
    if planet in _NOCTURNAL_PLANETS:
        return PlanetSect.NOCTURNAL
    # Mercury — by orientality; neutral follows the chart's sect.
    orientality = planet_orientality(planet, positions)
    if orientality is Orientality.ORIENTAL:
        return PlanetSect.DIURNAL
    if orientality is Orientality.OCCIDENTAL:
        return PlanetSect.NOCTURNAL
    return PlanetSect.DIURNAL if is_diurnal_chart else PlanetSect.NOCTURNAL


def _planet_is_masculine(
    planet: Planet,
    positions: Mapping[Planet, PlanetPosition],
) -> bool:
    if planet in _MASCULINE_PLANETS:
        return True
    if planet in _FEMININE_PLANETS:
        return False
    # Mercury — masculine when oriental, feminine when occidental (default
    # masculine when neutral).
    return planet_orientality(planet, positions) is not Orientality.OCCIDENTAL


def compute_sect_statuses(
    positions: Mapping[Planet, PlanetPosition],
    *,
    ascendant: float,
    is_diurnal: bool,
) -> dict[Planet, SectStatus]:
    """Sect / halb / hayz status for every classical planet in `positions`."""
    out: dict[Planet, SectStatus] = {}
    for planet, pp in positions.items():
        if not planet.is_classical:
            continue
        longitude = float(pp.position.longitude)
        sect = _planet_sect(planet, positions, is_diurnal)
        above = _is_above_horizon(longitude, ascendant)
        in_sect = (sect is PlanetSect.DIURNAL) == is_diurnal

        if sect is PlanetSect.DIURNAL:
            halb = above if is_diurnal else not above
        else:
            halb = not above if is_diurnal else above

        masculine = _planet_is_masculine(planet, positions)
        gender_match = masculine == _sign_is_masculine(longitude)
        out[planet] = SectStatus(
            planet=planet,
            planet_sect=sect,
            in_sect=in_sect,
            above_horizon=above,
            in_halb=halb,
            in_hayz=halb and gender_match,
            masculine=masculine,
            sign_gender_match=gender_match,
        )
    return out
