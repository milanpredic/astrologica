"""Decennials (Valens decennia) — sect-conditional time-lord technique.

Each of the seven classical planets rules a uniform major period of
**10 years 9 months** (10.75y; 129 months). The sequence starts with the
sect light (Sun for diurnal, Moon for nocturnal) and proceeds in descending
Chaldean order; one full cycle of 7 planets is 75y3m. Each major period
subdivides into 7 sub-periods (~1y 6m 12d each).
"""

from astrologica._internal.domain.decennials.compute import compute_decennials
from astrologica._internal.domain.decennials.types import (
    DecennialPeriod,
    DecennialSubPeriod,
)

__all__ = ["DecennialPeriod", "DecennialSubPeriod", "compute_decennials"]
