"""Public facade for solar, lunar, and Saturn returns.

A solar return is the chart for the exact moment in a given year when the
Sun returns to its natal ecliptic longitude (≈ the birthday, ±1 day). A
lunar return is the analogous event for the Moon (every ≈27.3 days). A
Saturn return is the moment Saturn revisits its natal longitude
(every ≈29.5 years).

Solar / lunar returns reuse the natal chart's tradition / ayanamsa / frame.
`place` defaults to the natal place; passing a different `Place` yields a
relocated return.

`compute_saturn_return` returns the exact datetime of the n-th return
(n=1 is the first, ~age 29.5).
"""

from __future__ import annotations

from datetime import datetime

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.lunar_return import compute_lunar_return as _compute_lunar_return
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.saturn_return import (
    compute_saturn_return as _compute_saturn_return,
)
from astrologica._internal.domain.solar_return import compute_solar_return as _compute_solar_return
from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter
from astrologica._internal.ports.ephemeris import EphemerisPort

__all__ = ["compute_lunar_return", "compute_saturn_return", "compute_solar_return"]


def compute_solar_return(
    natal: Chart,
    year: int,
    ephemeris: EphemerisPort | None = None,
    place: Place | None = None,
) -> Chart:
    """Solar return chart for `year`."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_solar_return(natal, year, adapter, place=place)


def compute_lunar_return(
    natal: Chart,
    after: datetime,
    ephemeris: EphemerisPort | None = None,
    place: Place | None = None,
) -> Chart:
    """Next lunar return chart on or after `after`."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_lunar_return(natal, after, adapter, place=place)


def compute_saturn_return(
    natal: Chart,
    n: int = 1,
    ephemeris: EphemerisPort | None = None,
) -> datetime | None:
    """The exact moment of the `n`-th Saturn return (n=1 is the first, ~age 29.5)."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_saturn_return(natal, n, adapter)
