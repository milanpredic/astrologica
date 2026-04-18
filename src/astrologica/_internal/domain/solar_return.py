"""compute_solar_return — solar return chart for a given calendar year.

A solar return (Latin: *revolutio solaris*) is the chart cast for the exact
moment in a given year when the Sun returns to its natal ecliptic longitude.
It lies within ±1 day of the birthday and traditionally serves as the base
chart for that year's unfolding themes.

Algorithm: bracket between birthday-1d and birthday+2d, bisect on `sin(Δlon)`
where `Δlon = transit_sun_lon − natal_sun_lon`. `sin` has zero-crossings both
where the Sun returns (Δlon = 0) and opposite (Δlon = 180°); since the Sun
moves <2° in the bracket window, only the Δlon=0 crossing is reachable.
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


def _jd_to_utc(jd_ut: float) -> datetime:
    seconds = (jd_ut - _JD_UNIX_EPOCH) * 86400.0
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)


def compute_solar_return(
    natal: Chart,
    year: int,
    ephemeris: EphemerisPort,
    place: Place | None = None,
) -> Chart:
    """Return the solar return chart for `year`.

    Uses the natal chart's tradition/ayanamsa/frame for consistency. `place`
    defaults to the natal place; pass a different `Place` for a relocated
    solar return.
    """
    natal_sun_lon = float(natal.planets[Planet.SUN].longitude)
    ayanamsa = natal.data.ayanamsa
    frame = natal.data.frame
    sr_place = place if place is not None else natal.data.place

    # Approximate the birthday in `year` as the same month/day at noon UTC.
    natal_utc = natal.data.utc
    try:
        approx = natal_utc.replace(year=year)
    except ValueError:
        # Feb 29 → use Feb 28 as the approximate target if year isn't a leap year.
        approx = natal_utc.replace(year=year, day=28)

    jd_approx = julian_day(approx)

    def residual(jd: float) -> float:
        lon = float(
            ephemeris.body_position(
                Planet.SUN, jd, ayanamsa=ayanamsa, frame=frame, place=sr_place
            ).longitude
        )
        return math.sin(math.radians(lon - natal_sun_lon))

    lo = jd_approx - 1.5
    hi = jd_approx + 1.5
    f_lo, f_hi = residual(lo), residual(hi)
    if f_lo * f_hi > 0.0:
        # Extend the window if the sign didn't flip.
        for _ in range(3):
            lo -= 1.0
            hi += 1.0
            f_lo, f_hi = residual(lo), residual(hi)
            if f_lo * f_hi <= 0.0:
                break
        else:
            raise RuntimeError("failed to bracket a solar return near the birthday")

    # Bisect to ~1 second (1 / 86400 of a day).
    tol = 1.0 / 86400.0
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

    sr_data = ChartData(
        datetime=event_utc,
        place=sr_place,
        ayanamsa=ayanamsa,
        frame=frame,
    )
    return compute_natal_chart(sr_data, natal.house_system, ephemeris, tradition=natal.tradition)
