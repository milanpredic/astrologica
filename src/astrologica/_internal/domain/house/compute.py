"""compute_house_cusps — the 12 house cusps + ascendant + midheaven."""

from __future__ import annotations

from datetime import datetime

from astrologica._internal.domain.ayanamsa import Ayanamsa
from astrologica._internal.domain.house.cusp import HouseCusp
from astrologica._internal.domain.house.house import House
from astrologica._internal.domain.house.system import HouseSystem
from astrologica._internal.domain.measures.angle import Longitude
from astrologica._internal.domain.measures.jd import julian_day
from astrologica._internal.domain.place import Place
from astrologica._internal.ports.ephemeris import EphemerisPort


def compute_house_cusps(
    when: datetime,
    place: Place,
    system: HouseSystem,
    ephemeris: EphemerisPort,
    ayanamsa: Ayanamsa | None = None,
) -> tuple[tuple[HouseCusp, ...], Longitude, Longitude]:
    """Return (house cusps, ascendant, midheaven) for a moment and a place.

    `when` must be timezone-aware. Output cusps are ordered 1..12. `ayanamsa=None`
    means tropical; otherwise the cusps are sidereal relative to that ayanamsa.
    """
    if when.tzinfo is None:
        raise ValueError("compute_house_cusps requires a timezone-aware datetime")

    jd = julian_day(when)
    raw = ephemeris.house_cusps(jd, place, system, ayanamsa=ayanamsa)
    cusps = tuple(HouseCusp(house=House(i + 1), cusp=Longitude(raw.cusps[i])) for i in range(12))
    return cusps, Longitude(raw.ascendant), Longitude(raw.midheaven)
