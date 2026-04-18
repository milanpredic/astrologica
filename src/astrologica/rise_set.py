"""Public facade for rise / set / MC / IC event times."""

from __future__ import annotations

from datetime import date

from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.rise_set import RiseSetTimes
from astrologica._internal.domain.rise_set import compute_rise_set as _compute_rise_set
from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter
from astrologica._internal.ports.ephemeris import EphemerisPort

__all__ = ["RiseSetTimes", "compute_rise_set"]


def compute_rise_set(
    body: Planet,
    on: date,
    place: Place,
    ephemeris: EphemerisPort | None = None,
) -> RiseSetTimes:
    """Horizon events (rise, MC, set, IC) for `body` on `on` at `place`."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_rise_set(body, on, place, adapter)
