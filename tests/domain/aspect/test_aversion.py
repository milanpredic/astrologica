"""is_in_aversion_to — no Ptolemaic aspect within default orbs."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from astrologica import ChartData, Place, Planet, compute_natal_chart

pytestmark = pytest.mark.infrastructure


def _sample_chart():
    return compute_natal_chart(
        ChartData(
            datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("America/New_York")),
            place=Place(latitude=40.7128, longitude=-74.0060),
        )
    )


def test_aversion_self_is_not_in_aversion_to_self() -> None:
    from astrologica._internal.domain.aspect.aversion import is_in_aversion_to

    chart = _sample_chart()
    for planet in (Planet.SUN, Planet.MOON, Planet.MARS):
        assert not is_in_aversion_to(planet, planet, chart)


def test_aversion_returns_bool() -> None:
    from astrologica._internal.domain.aspect.aversion import is_in_aversion_to

    chart = _sample_chart()
    result = is_in_aversion_to(Planet.SUN, Planet.MARS, chart)
    assert isinstance(result, bool)
