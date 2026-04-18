"""EphemerisPort — the only interface by which domain code talks to astronomical data.

Concrete implementations live in `_internal/infrastructure/ephemeris/`. Only they
may import third-party ephemeris libraries (pyswisseph, Skyfield, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from astrologica._internal.domain.ayanamsa import Ayanamsa
from astrologica._internal.domain.house.system import HouseSystem
from astrologica._internal.domain.measures.ecliptic import EclipticPosition
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.reference_frame import ReferenceFrame


@dataclass(frozen=True, slots=True)
class RawHouseCusps:
    """Raw house-system output: the 12 cusps + ascendant + midheaven (all longitudes)."""

    cusps: tuple[float, float, float, float, float, float, float, float, float, float, float, float]
    ascendant: float
    midheaven: float


class EphemerisPort(Protocol):
    """What the domain needs from an ephemeris backend.

    - `ayanamsa=None` means tropical output (default). An `Ayanamsa` returns
      sidereal longitudes relative to that zodiac reference.
    - `frame` selects the observer frame (geocentric default; topocentric needs
      `place` to include altitude; heliocentric makes the Sun ~0°).
    """

    def body_position(
        self,
        planet: Planet,
        jd_ut: float,
        ayanamsa: Ayanamsa | None = None,
        frame: ReferenceFrame = ReferenceFrame.GEOCENTRIC,
        place: Place | None = None,
    ) -> EclipticPosition:
        """Ecliptic position of a planet at a given Julian Day (UT).

        `place` is only consulted for `TOPOCENTRIC` — it supplies the observer
        coordinates (lat/lon/altitude). For `GEOCENTRIC` / `HELIOCENTRIC` it is
        ignored.
        """
        ...

    def house_cusps(
        self,
        jd_ut: float,
        place: Place,
        system: HouseSystem,
        ayanamsa: Ayanamsa | None = None,
    ) -> RawHouseCusps:
        """The 12 house cusps + ascendant + midheaven for a moment and a place.

        House cusps are inherently observer-on-Earth quantities; `frame` does
        not apply here (ASC/MC are geocentric-topocentric in practice, always
        computed relative to the provided `place`).
        """
        ...

    def last_lunation_before(self, jd_ut: float) -> tuple[float, float]:
        """Return (jd_of_event, moon_longitude) of the most recent new OR full moon before `jd_ut`.

        The sign of `moon_longitude - sun_longitude_at_event` (taken mod 360 and reduced to
        [-180, 180]) tells the caller whether it was a new moon (≈0°) or full moon (≈±180°).
        Lunations are tropical and geocentric — they don't change with ayanamsa or frame.
        """
        ...

    def next_rise(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        """Next rise (body crossing the eastern horizon) after `jd_ut_after`.

        Returns the Julian Day of the event, or `None` if the body is circumpolar
        (never rises or sets at this latitude during the search window).
        """
        ...

    def next_set(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        """Next set (body crossing the western horizon) after `jd_ut_after`."""
        ...

    def next_mc_transit(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        """Next upper meridian transit (body crossing the MC) after `jd_ut_after`."""
        ...

    def next_ic_transit(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        """Next lower meridian transit (body crossing the IC) after `jd_ut_after`."""
        ...

    def fixed_star_longitude(
        self,
        name: str,
        jd_ut: float,
        ayanamsa: Ayanamsa | None = None,
    ) -> float:
        """Ecliptic longitude of a fixed star at a given Julian Day (UT).

        `name` is the Swiss Ephemeris catalog name (e.g. `"aldebaran"`). When
        `ayanamsa` is set, the longitude is sidereal.
        """
        ...
