"""Public-facade smoke test for astrologica.solar_state."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.pure


def test_solar_state_facade_exports() -> None:
    from astrologica.solar_state import (  # noqa: F401
        SOLAR_STATE_THRESHOLDS,
        SolarState,
        SolarStateThresholds,
        planet_solar_state,
    )
