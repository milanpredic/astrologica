"""SwissEphemerisAdapter — concrete EphemerisPort backed by pyswisseph."""

from __future__ import annotations

import math
from pathlib import Path

import swisseph as swe

from astrologica._internal.domain.ayanamsa import Ayanamsa
from astrologica._internal.domain.house.system import HouseSystem
from astrologica._internal.domain.measures.angle import Latitude, Longitude
from astrologica._internal.domain.measures.ecliptic import EclipticPosition, Speed
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.reference_frame import ReferenceFrame
from astrologica._internal.ports.ephemeris import EphemerisPort, RawHouseCusps

# Direct mapping from Planet enum → pyswisseph body ID.
# South nodes are derived from their north-node counterparts (+180° in longitude,
# mirrored latitude, same speed) — there's no Swiss Eph ID for them.
_SWE_BODY: dict[Planet, int] = {
    Planet.SUN: swe.SUN,
    Planet.MOON: swe.MOON,
    Planet.MERCURY: swe.MERCURY,
    Planet.VENUS: swe.VENUS,
    Planet.MARS: swe.MARS,
    Planet.JUPITER: swe.JUPITER,
    Planet.SATURN: swe.SATURN,
    Planet.URANUS: swe.URANUS,
    Planet.NEPTUNE: swe.NEPTUNE,
    Planet.PLUTO: swe.PLUTO,
    Planet.TRUE_NODE: swe.TRUE_NODE,
    Planet.MEAN_NODE: swe.MEAN_NODE,
}

# North-node → south-node pairing: a south node is exactly the antipode of its
# corresponding north node on the ecliptic.
_SOUTH_NODE_OF: dict[Planet, Planet] = {
    Planet.SOUTH_TRUE_NODE: Planet.TRUE_NODE,
    Planet.SOUTH_MEAN_NODE: Planet.MEAN_NODE,
}

# Domain Ayanamsa → Swiss Eph SIDM_* constant.
_SWE_AYANAMSA: dict[Ayanamsa, int] = {
    Ayanamsa.FAGAN_BRADLEY: swe.SIDM_FAGAN_BRADLEY,
    Ayanamsa.LAHIRI: swe.SIDM_LAHIRI,
    Ayanamsa.DELUCE: swe.SIDM_DELUCE,
    Ayanamsa.RAMAN: swe.SIDM_RAMAN,
    Ayanamsa.USHASHASHI: swe.SIDM_USHASHASHI,
    Ayanamsa.KRISHNAMURTI: swe.SIDM_KRISHNAMURTI,
    Ayanamsa.DJWHAL_KHUL: swe.SIDM_DJWHAL_KHUL,
    Ayanamsa.YUKTESHWAR: swe.SIDM_YUKTESHWAR,
    Ayanamsa.JN_BHASIN: swe.SIDM_JN_BHASIN,
    Ayanamsa.BABYL_KUGLER1: swe.SIDM_BABYL_KUGLER1,
    Ayanamsa.BABYL_KUGLER2: swe.SIDM_BABYL_KUGLER2,
    Ayanamsa.BABYL_KUGLER3: swe.SIDM_BABYL_KUGLER3,
    Ayanamsa.BABYL_HUBER: swe.SIDM_BABYL_HUBER,
    Ayanamsa.BABYL_ETPSC: swe.SIDM_BABYL_ETPSC,
    Ayanamsa.ALDEBARAN_15TAU: swe.SIDM_ALDEBARAN_15TAU,
    Ayanamsa.HIPPARCHOS: swe.SIDM_HIPPARCHOS,
    Ayanamsa.SASSANIAN: swe.SIDM_SASSANIAN,
    Ayanamsa.GALCENT_0SAG: swe.SIDM_GALCENT_0SAG,
    Ayanamsa.J2000: swe.SIDM_J2000,
    Ayanamsa.J1900: swe.SIDM_J1900,
    Ayanamsa.B1950: swe.SIDM_B1950,
}

# Base flag: Moshier built-in ephemeris with speed. Sidereal flag is ORed on top
# when the caller supplies an ayanamsa.
_BASE_FLAGS: int = swe.FLG_MOSEPH | swe.FLG_SPEED


def _flags_for(
    ayanamsa: Ayanamsa | None,
    frame: ReferenceFrame = ReferenceFrame.GEOCENTRIC,
) -> int:
    flags = _BASE_FLAGS
    if ayanamsa is not None:
        flags |= swe.FLG_SIDEREAL
    if frame is ReferenceFrame.TOPOCENTRIC:
        flags |= swe.FLG_TOPOCTR
    elif frame is ReferenceFrame.HELIOCENTRIC:
        flags |= swe.FLG_HELCTR
    return int(flags)


def _configure_sid_mode(ayanamsa: Ayanamsa | None) -> None:
    if ayanamsa is not None:
        swe.set_sid_mode(_SWE_AYANAMSA[ayanamsa], 0.0, 0.0)


def _configure_topo(frame: ReferenceFrame, place: Place | None) -> None:
    if frame is ReferenceFrame.TOPOCENTRIC:
        if place is None:
            raise ValueError("TOPOCENTRIC frame requires a `place` to locate the observer")
        swe.set_topo(place.longitude, place.latitude, place.altitude)


# Resolve the bundled `_data/` directory relative to this infrastructure
# module: src/astrologica/_internal/infrastructure/ephemeris/swiss.py →
# up 3 levels gets to src/astrologica/, then append `_data`.
_BUNDLED_DATA_DIR: str = str((Path(__file__).resolve().parents[3] / "_data").resolve())


class SwissEphemerisAdapter(EphemerisPort):
    """Swiss Ephemeris-backed implementation. Uses the Moshier built-in
    ephemeris for planet positions (no data files required), but points Swiss
    Ephemeris at a bundled data directory so fixed-star lookups work
    out-of-the-box.

    The bundled directory ships a minimal `sefstars.txt` covering the 30
    classical `FixedStar` enum members. High-precision `.se1` files for
    planet positions are *not* bundled (they're proprietary and large); if a
    caller wants them they can pass `ephe_path` pointing at a local install.
    """

    def __init__(self, ephe_path: str | None = None) -> None:
        swe.set_ephe_path(ephe_path if ephe_path is not None else _BUNDLED_DATA_DIR)

    # ---- body positions ---------------------------------------------------

    def body_position(
        self,
        planet: Planet,
        jd_ut: float,
        ayanamsa: Ayanamsa | None = None,
        frame: ReferenceFrame = ReferenceFrame.GEOCENTRIC,
        place: Place | None = None,
    ) -> EclipticPosition:
        if planet in _SOUTH_NODE_OF:
            # South node: antipode of the corresponding north node. Sidereal offset
            # cancels in the subtraction, so we can safely derive after rotation.
            north = self.body_position(
                _SOUTH_NODE_OF[planet], jd_ut, ayanamsa=ayanamsa, frame=frame, place=place
            )
            return EclipticPosition(
                longitude=Longitude((float(north.longitude) + 180.0) % 360.0),
                latitude=Latitude(-float(north.latitude)),
                speed=Speed(float(north.speed)),
            )

        _configure_sid_mode(ayanamsa)
        _configure_topo(frame, place)
        xx, _retflags = swe.calc_ut(jd_ut, _SWE_BODY[planet], _flags_for(ayanamsa, frame))
        return EclipticPosition(
            longitude=Longitude(xx[0]),
            latitude=Latitude(xx[1]),
            speed=Speed(xx[3]),
        )

    # ---- house cusps ------------------------------------------------------

    def house_cusps(
        self,
        jd_ut: float,
        place: Place,
        system: HouseSystem,
        ayanamsa: Ayanamsa | None = None,
    ) -> RawHouseCusps:
        _configure_sid_mode(ayanamsa)
        cusps, ascmc = swe.houses_ex(
            jd_ut,
            place.latitude,
            place.longitude,
            system.value.encode("ascii"),
            _flags_for(ayanamsa),
        )
        twelve: tuple[
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
            cusps[0],
            cusps[1],
            cusps[2],
            cusps[3],
            cusps[4],
            cusps[5],
            cusps[6],
            cusps[7],
            cusps[8],
            cusps[9],
            cusps[10],
            cusps[11],
        )
        return RawHouseCusps(cusps=twelve, ascendant=ascmc[0], midheaven=ascmc[1])

    # ---- rise / set / transit --------------------------------------------

    def _rise_trans(
        self,
        body: Planet,
        jd_ut_after: float,
        place: Place,
        rsmi: int,
    ) -> float | None:
        if body in _SOUTH_NODE_OF:
            # The south node is a derived point with no physical body to rise/set.
            return None
        res, tret = swe.rise_trans(
            jd_ut_after,
            _SWE_BODY[body],
            rsmi,
            (place.longitude, place.latitude, place.altitude),
            0.0,
            0.0,
            _BASE_FLAGS,
        )
        if res < 0:
            return None
        return float(tret[0])

    def next_rise(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        return self._rise_trans(body, jd_ut_after, place, swe.CALC_RISE)

    def next_set(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        return self._rise_trans(body, jd_ut_after, place, swe.CALC_SET)

    def next_mc_transit(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        return self._rise_trans(body, jd_ut_after, place, swe.CALC_MTRANSIT)

    def next_ic_transit(self, body: Planet, jd_ut_after: float, place: Place) -> float | None:
        return self._rise_trans(body, jd_ut_after, place, swe.CALC_ITRANSIT)

    # ---- fixed stars ------------------------------------------------------

    def fixed_star_longitude(
        self,
        name: str,
        jd_ut: float,
        ayanamsa: Ayanamsa | None = None,
    ) -> float:
        _configure_sid_mode(ayanamsa)
        xx, _stnam, _retflags = swe.fixstar_ut(name, jd_ut, _flags_for(ayanamsa))
        return float(xx[0])

    # ---- last lunation (new or full moon) ---------------------------------

    def last_lunation_before(self, jd_ut: float) -> tuple[float, float]:
        """Walk back from `jd_ut` in 1-day steps, bracketing a zero of sin(lon_moon - lon_sun).

        `sin(elongation)` crosses zero at both new moons (elongation ≈ 0°) and full moons
        (≈ 180°) — so the first sign-change while stepping backwards picks up the most
        recent lunation of either kind. Refined via 30 bisection rounds (~sub-minute).
        Lunation geometry is ayanamsa-invariant, so always uses tropical base flags.
        """

        def sin_elongation(t: float) -> float:
            moon_lon = swe.calc_ut(t, swe.MOON, _BASE_FLAGS)[0][0]
            sun_lon = swe.calc_ut(t, swe.SUN, _BASE_FLAGS)[0][0]
            delta = (moon_lon - sun_lon) % 360.0
            return math.sin(math.radians(delta))

        t_hi = jd_ut
        f_hi = sin_elongation(t_hi)
        t_lo = t_hi
        f_lo = f_hi
        for _ in range(40):  # moon cycle is ~29.5 days, step-size is 1 day
            t_lo = t_hi - 1.0
            f_lo = sin_elongation(t_lo)
            if f_lo * f_hi <= 0.0:
                break
            t_hi, f_hi = t_lo, f_lo
        else:  # pragma: no cover - should never happen within 40 days
            raise RuntimeError("failed to bracket a lunation within 40 days")

        lo, hi = t_lo, t_hi
        f_lo_v = f_lo
        for _ in range(30):
            mid = (lo + hi) / 2.0
            f_mid = sin_elongation(mid)
            if f_lo_v * f_mid <= 0.0:
                hi = mid
            else:
                lo, f_lo_v = mid, f_mid
        event_jd = (lo + hi) / 2.0
        moon_lon = swe.calc_ut(event_jd, swe.MOON, _BASE_FLAGS)[0][0]
        return event_jd, moon_lon
