"""Solar state classification — cazimi / combust / under-beams / free.

The package exposes only types from `__init__` to avoid an import cycle with
`planet.position` (which embeds `SolarState` as a field). Consumers of
`planet_solar_state` import from the `compute` submodule.
"""

from astrologica._internal.domain.solar_state.types import (
    SOLAR_STATE_THRESHOLDS,
    SolarState,
    SolarStateThresholds,
)

__all__ = ["SOLAR_STATE_THRESHOLDS", "SolarState", "SolarStateThresholds"]
