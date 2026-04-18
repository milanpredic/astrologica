"""compute_planet_positions — ecliptic positions for a chosen set of bodies."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime

from astrologica._internal.domain.ayanamsa import Ayanamsa
from astrologica._internal.domain.measures.jd import julian_day
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition
from astrologica._internal.domain.reference_frame import ReferenceFrame
from astrologica._internal.ports.ephemeris import EphemerisPort


def compute_planet_positions(
    when: datetime,
    ephemeris: EphemerisPort,
    bodies: Iterable[Planet] | None = None,
    ayanamsa: Ayanamsa | None = None,
    frame: ReferenceFrame = ReferenceFrame.GEOCENTRIC,
    place: Place | None = None,
) -> Mapping[Planet, PlanetPosition]:
    """Return positions of `bodies` at `when`.

    `when` must be timezone-aware; it's converted to UTC internally, then to a
    Julian Day for the ephemeris query. `bodies` defaults to the 7 classical
    planets when `None` (the traditional-astrology default). `ayanamsa=None`
    means tropical output; an `Ayanamsa` shifts to the sidereal zodiac. `frame`
    selects the observer frame; `TOPOCENTRIC` requires `place`.
    """
    if when.tzinfo is None:
        raise ValueError("compute_planet_positions requires a timezone-aware datetime")

    selected = Planet.classical() if bodies is None else frozenset(bodies)

    jd = julian_day(when)
    return {
        planet: PlanetPosition(
            planet=planet,
            position=ephemeris.body_position(
                planet, jd, ayanamsa=ayanamsa, frame=frame, place=place
            ),
        )
        for planet in selected
    }
