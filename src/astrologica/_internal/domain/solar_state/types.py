"""Solar-state types — enum + threshold defaults, no chart dependency."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SolarState(Enum):
    """A planet's solar state: distance from the Sun in ecliptic longitude."""

    FREE = "free"
    UNDER_BEAMS = "under_beams"
    COMBUST = "combust"
    CAZIMI = "cazimi"


@dataclass(frozen=True, slots=True)
class SolarStateThresholds:
    """Boundary distances between solar states.

    `cazimi_arcminutes` is in arcminutes (default 17.0 → 0°17').
    `combust_degrees` and `under_beams_degrees` are in decimal degrees.
    """

    cazimi_arcminutes: float = 17.0
    combust_degrees: float = 8.5
    under_beams_degrees: float = 17.0


SOLAR_STATE_THRESHOLDS: SolarStateThresholds = SolarStateThresholds()
