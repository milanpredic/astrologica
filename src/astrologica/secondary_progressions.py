"""Public facade for secondary (day-for-year) progressions."""

from __future__ import annotations

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.secondary_progressions import (
    compute_secondary_progressions as _compute_secondary_progressions,
)
from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter
from astrologica._internal.ports.ephemeris import EphemerisPort

__all__ = ["compute_secondary_progressions"]


def compute_secondary_progressions(
    natal: Chart,
    age_years: float,
    ephemeris: EphemerisPort | None = None,
) -> Chart:
    """Progressed chart for age `age_years` (day-for-a-year key)."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_secondary_progressions(natal, age_years, adapter)
