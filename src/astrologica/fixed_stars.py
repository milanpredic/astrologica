"""Public facade for fixed-star conjunctions."""

from __future__ import annotations

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.fixed_stars import (
    FixedStarConjunction,
)
from astrologica._internal.domain.fixed_stars import (
    compute_fixed_star_conjunctions as _compute_fixed_star_conjunctions,
)
from astrologica._internal.domain.fixed_stars_enum import FixedStar
from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter
from astrologica._internal.ports.ephemeris import EphemerisPort

__all__ = ["FixedStar", "FixedStarConjunction", "compute_fixed_star_conjunctions"]


def compute_fixed_star_conjunctions(
    chart: Chart,
    orb: float = 1.0,
    ephemeris: EphemerisPort | None = None,
) -> tuple[FixedStarConjunction, ...]:
    """Conjunctions between chart bodies and the 30 classical fixed stars."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_fixed_star_conjunctions(chart, adapter, orb=orb)
