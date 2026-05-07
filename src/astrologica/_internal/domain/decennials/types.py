"""Decennial period type."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.planet.planet import Planet


@dataclass(frozen=True, slots=True)
class DecennialPeriod:
    """A major period in the Valens decennial sequence."""

    ruler: Planet
    start_age: float
    end_age: float
