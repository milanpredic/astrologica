"""find_time — solve for when a body crosses a target longitude.

Bracketed root search between `start` and `end`, bisected to ~1-minute
precision. Uses `sin(Δλ)` as residual; disambiguates between the target
longitude and its antipode after each root using actual separation.

Returns `None` if no crossing is found in the window.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

from astrologica._internal.domain.ayanamsa import Ayanamsa
from astrologica._internal.domain.measures.jd import julian_day
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.reference_frame import ReferenceFrame
from astrologica._internal.ports.ephemeris import EphemerisPort

_JD_UNIX_EPOCH = 2440587.5


def _jd_to_utc(jd_ut: float) -> datetime:
    seconds = (jd_ut - _JD_UNIX_EPOCH) * 86400.0
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)


def _step_days_for(body: Planet) -> float:
    if body is Planet.MOON:
        return 0.25
    if body in (Planet.SUN, Planet.MERCURY, Planet.VENUS, Planet.MARS):
        return 1.0
    return 2.0


def find_time(
    body: Planet,
    target_longitude: float,
    start: datetime,
    end: datetime,
    ephemeris: EphemerisPort,
    ayanamsa: Ayanamsa | None = None,
    frame: ReferenceFrame = ReferenceFrame.GEOCENTRIC,
    place: Place | None = None,
) -> datetime | None:
    """First moment in `[start, end]` when `body` crosses `target_longitude`.

    Returns `None` if no crossing occurs in the window. The window must
    already be wide enough to contain the crossing (for planets like Saturn,
    a crossing may be months away).
    """
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("find_time requires timezone-aware start/end")
    if end <= start:
        return None

    jd_start = julian_day(start.astimezone(UTC))
    jd_end = julian_day(end.astimezone(UTC))
    target = target_longitude % 360.0

    def lon(jd: float) -> float:
        return float(
            ephemeris.body_position(body, jd, ayanamsa=ayanamsa, frame=frame, place=place).longitude
        )

    def residual(jd: float) -> float:
        return math.sin(math.radians(lon(jd) - target))

    def is_near_target(jd: float) -> bool:
        diff = (lon(jd) - target + 180.0) % 360.0 - 180.0
        return abs(diff) < 5.0

    step = _step_days_for(body)
    jd = jd_start
    prev_val = residual(jd)
    while jd < jd_end:
        jd_next = min(jd + step, jd_end)
        val = residual(jd_next)
        # Guard against sin-wrap discontinuity by checking sep differences —
        # we require near-target to accept a root.
        if prev_val * val <= 0.0:
            # Bisect.
            lo, hi = jd, jd_next
            f_lo = prev_val
            tol = 1.0 / 1440.0  # 1 minute
            for _ in range(60):
                mid = (lo + hi) / 2.0
                f_mid = residual(mid)
                if (hi - lo) < tol:
                    break
                if f_lo * f_mid <= 0.0:
                    hi = mid
                else:
                    lo, f_lo = mid, f_mid
            root = (lo + hi) / 2.0
            if is_near_target(root):
                return _jd_to_utc(root)
            # else: it was the antipode; keep searching.
        prev_val = val
        jd = jd_next

    return None
