"""compute_saturn_return — find the n-th Saturn return after birth.

Saturn's mean sidereal period is ~29.4571 years. The function locates the
exact moment Saturn returns to its natal ecliptic longitude by bracketing
a ±3-year window around the expected return and delegating to find_time.

Returns None if no crossing is found in the window (rare — Saturn's path
is monotonic enough for this to always succeed).
"""

from __future__ import annotations

from datetime import datetime, timedelta

from astrologica._internal.domain.find_time import find_time as _find_time
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.ports.ephemeris import EphemerisPort

_SATURN_PERIOD_DAYS: float = 29.4571 * 365.25
_SEARCH_HALF_WINDOW_DAYS: float = 3.0 * 365.25


def compute_saturn_return(
    natal: object,
    n: int,
    ephemeris: EphemerisPort,
) -> datetime | None:
    """The exact moment of the `n`-th Saturn return (n=1 is the first, ~age 29.5)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")

    natal_when: datetime = getattr(natal, "data").datetime
    natal_saturn_lon = float(getattr(natal, "planets")[Planet.SATURN].position.longitude)

    expected = natal_when + timedelta(days=_SATURN_PERIOD_DAYS * n)
    start = expected - timedelta(days=_SEARCH_HALF_WINDOW_DAYS)
    end = expected + timedelta(days=_SEARCH_HALF_WINDOW_DAYS)

    ayanamsa = getattr(natal, "data").ayanamsa
    frame = getattr(natal, "data").frame
    place = getattr(natal, "data").place

    return _find_time(
        Planet.SATURN,
        natal_saturn_lon,
        start,
        end,
        ephemeris,
        ayanamsa=ayanamsa,
        frame=frame,
        place=place,
    )
