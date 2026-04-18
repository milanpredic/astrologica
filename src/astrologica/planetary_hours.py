"""Public facade for Chaldean-order planetary hours."""

from __future__ import annotations

from datetime import date

from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planetary_hours import (
    PlanetaryHour,
)
from astrologica._internal.domain.planetary_hours import (
    compute_planetary_hours as _compute_planetary_hours,
)
from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter
from astrologica._internal.ports.ephemeris import EphemerisPort

__all__ = ["PlanetaryHour", "compute_planetary_hours"]


def compute_planetary_hours(
    on: date,
    place: Place,
    ephemeris: EphemerisPort | None = None,
) -> tuple[PlanetaryHour, ...]:
    """Return the 24 planetary hours for the local day `on` at `place`."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_planetary_hours(on, place, adapter)
