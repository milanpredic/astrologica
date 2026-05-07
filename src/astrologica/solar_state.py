"""Public facade for solar-state classification."""

from astrologica._internal.domain.solar_state.compute import planet_solar_state
from astrologica._internal.domain.solar_state.types import (
    SOLAR_STATE_THRESHOLDS,
    SolarState,
    SolarStateThresholds,
)

__all__ = [
    "SOLAR_STATE_THRESHOLDS",
    "SolarState",
    "SolarStateThresholds",
    "planet_solar_state",
]
