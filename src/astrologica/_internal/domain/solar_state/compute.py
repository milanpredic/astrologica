"""Classify a planet's relationship to the Sun by ecliptic separation."""

from __future__ import annotations

from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition
from astrologica._internal.domain.solar_state.types import (
    SOLAR_STATE_THRESHOLDS,
    SolarState,
    SolarStateThresholds,
)

__all__ = ["SOLAR_STATE_THRESHOLDS", "SolarState", "SolarStateThresholds", "planet_solar_state"]


def planet_solar_state(
    planet_pos: PlanetPosition,
    sun_pos: PlanetPosition,
    *,
    thresholds: SolarStateThresholds = SOLAR_STATE_THRESHOLDS,
) -> SolarState:
    """Classify `planet_pos` by ecliptic separation from `sun_pos`.

    Boundaries (default thresholds):
      separation < 0°17'  → CAZIMI
      separation < 8°30'  → COMBUST
      separation < 17°    → UNDER_BEAMS
      otherwise           → FREE

    The Sun itself returns FREE.
    """
    if planet_pos.planet is Planet.SUN:
        return SolarState.FREE

    sun_lon = float(sun_pos.position.longitude)
    pl_lon = float(planet_pos.position.longitude)
    diff = abs(((pl_lon - sun_lon) + 180.0) % 360.0 - 180.0)

    cazimi_deg = thresholds.cazimi_arcminutes / 60.0
    if diff < cazimi_deg:
        return SolarState.CAZIMI
    if diff < thresholds.combust_degrees:
        return SolarState.COMBUST
    if diff < thresholds.under_beams_degrees:
        return SolarState.UNDER_BEAMS
    return SolarState.FREE
