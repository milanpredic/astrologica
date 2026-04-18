"""compute_lunar_return — lunar return chart (Moon back at its natal longitude).

A lunar return occurs roughly every 27.3 days (the sidereal month). This
function returns the first lunar return on or after a given moment.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.chart.chart_data import ChartData
from astrologica._internal.domain.chart.compute import compute_natal_chart
from astrologica._internal.domain.measures.jd import julian_day
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.ports.ephemeris import EphemerisPort

_JD_UNIX_EPOCH = 2440587.5
_LUNAR_CYCLE_DAYS = 27.321661  # sidereal month


def _jd_to_utc(jd_ut: float) -> datetime:
    seconds = (jd_ut - _JD_UNIX_EPOCH) * 86400.0
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)


def compute_lunar_return(
    natal: Chart,
    after: datetime,
    ephemeris: EphemerisPort,
    place: Place | None = None,
) -> Chart:
    """Next lunar return chart on or after `after`.

    Uses the natal chart's tradition/ayanamsa/frame. `place` defaults to the
    natal place.
    """
    if after.tzinfo is None:
        raise ValueError("compute_lunar_return requires a timezone-aware `after`")

    natal_moon_lon = float(natal.planets[Planet.MOON].longitude)
    ayanamsa = natal.data.ayanamsa
    frame = natal.data.frame
    lr_place = place if place is not None else natal.data.place

    jd_after = julian_day(after.astimezone(UTC))

    def moon_lon(jd: float) -> float:
        return float(
            ephemeris.body_position(
                Planet.MOON, jd, ayanamsa=ayanamsa, frame=frame, place=lr_place
            ).longitude
        )

    def residual(jd: float) -> float:
        return math.sin(math.radians(moon_lon(jd) - natal_moon_lon))

    # Walk in 6h steps — the Moon covers ~3° per 6h, cleanly resolving the signal.
    step = 0.25
    t_lo = jd_after
    f_lo = residual(t_lo)
    t_hi = t_lo
    f_hi = f_lo
    max_steps = int((_LUNAR_CYCLE_DAYS + 3.0) / step) + 1
    for _ in range(max_steps):
        t_hi = t_lo + step
        f_hi = residual(t_hi)
        if f_lo * f_hi <= 0.0 and _is_near_target(moon_lon(t_hi), natal_moon_lon):
            break
        t_lo, f_lo = t_hi, f_hi
    else:  # pragma: no cover
        raise RuntimeError("failed to bracket a lunar return within a lunar cycle")

    # Bisect to ~1 second precision.
    tol = 1.0 / 86400.0
    lo, hi = t_lo, t_hi
    for _ in range(60):
        mid = (lo + hi) / 2.0
        f_mid = residual(mid)
        if (hi - lo) < tol:
            break
        if f_lo * f_mid <= 0.0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    event_jd = (lo + hi) / 2.0
    event_utc = _jd_to_utc(event_jd)

    lr_data = ChartData(
        datetime=event_utc,
        place=lr_place,
        ayanamsa=ayanamsa,
        frame=frame,
    )
    return compute_natal_chart(lr_data, natal.house_system, ephemeris, tradition=natal.tradition)


def _is_near_target(current_lon: float, target_lon: float) -> bool:
    """After a sign change in sin(Δlon), confirm Moon is near target, not antipode."""
    diff = (current_lon - target_lon + 180.0) % 360.0 - 180.0
    return abs(diff) < 10.0


__all__ = ["compute_lunar_return"]
