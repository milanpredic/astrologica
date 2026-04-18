"""In-memory EphemerisPort for deterministic unit tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from astrologica._internal.domain.ayanamsa import Ayanamsa
from astrologica._internal.domain.house.system import HouseSystem
from astrologica._internal.domain.measures.angle import Latitude, Longitude
from astrologica._internal.domain.measures.ecliptic import EclipticPosition, Speed
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.reference_frame import ReferenceFrame
from astrologica._internal.ports.ephemeris import EphemerisPort, RawHouseCusps


@dataclass
class FakeEphemeris(EphemerisPort):
    """Simple in-memory ephemeris for tests — each planet's longitude is fixed,
    latitude is 0, speed is configurable (defaults to direct motion).
    House cusps are generated as a regular 30° spacing starting from `ascendant`.
    """

    longitudes: dict[Planet, float] = field(default_factory=dict)
    speeds: dict[Planet, float] = field(default_factory=dict)
    star_longitudes: dict[str, float] = field(default_factory=dict)
    ascendant: float = 0.0
    midheaven: float = 270.0
    # Default JD ≈ J2000 so the _jd_to_utc conversion in syzygy compute doesn't
    # overflow for tests that don't care about the exact lunation moment.
    last_lunation_jd: float = 2451545.0
    last_lunation_moon_lon: float = 0.0

    def body_position(
        self,
        planet: Planet,
        jd_ut: float,
        ayanamsa: Ayanamsa | None = None,
        frame: ReferenceFrame = ReferenceFrame.GEOCENTRIC,
        place: Place | None = None,
    ) -> EclipticPosition:
        lon = self.longitudes.get(planet, 0.0)
        speed = self.speeds.get(planet, 1.0)
        return EclipticPosition(
            longitude=Longitude(lon),
            latitude=Latitude(0.0),
            speed=Speed(speed),
        )

    def house_cusps(
        self,
        jd_ut: float,
        place: Place,
        system: HouseSystem,
        ayanamsa: Ayanamsa | None = None,
    ) -> RawHouseCusps:
        cusps_list = [(self.ascendant + i * 30.0) % 360.0 for i in range(12)]
        cusps: tuple[
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
        ] = (
            cusps_list[0],
            cusps_list[1],
            cusps_list[2],
            cusps_list[3],
            cusps_list[4],
            cusps_list[5],
            cusps_list[6],
            cusps_list[7],
            cusps_list[8],
            cusps_list[9],
            cusps_list[10],
            cusps_list[11],
        )
        return RawHouseCusps(cusps=cusps, ascendant=self.ascendant, midheaven=self.midheaven)

    def last_lunation_before(self, jd_ut: float) -> tuple[float, float]:
        return self.last_lunation_jd, self.last_lunation_moon_lon

    # Rise / set / transit stubs — tests that exercise these should use the
    # real Swiss adapter.  Override in subclasses for custom behaviour.
    def next_rise(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        return None

    def next_set(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        return None

    def next_mc_transit(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        return None

    def next_ic_transit(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        return None

    # Fixed stars — prepopulate via `star_longitudes` on construction.
    # Unknown stars raise KeyError so tests don't accidentally conjoin a
    # body at 0° with a default-zero star longitude.
    def fixed_star_longitude(
        self, name: str, jd_ut: float, ayanamsa: Ayanamsa | None = None
    ) -> float:
        if name not in self.star_longitudes:
            raise KeyError(f"fake ephemeris has no longitude for star {name!r}")
        return self.star_longitudes[name]
