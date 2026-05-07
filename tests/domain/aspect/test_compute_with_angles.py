"""compute_aspects with include_angles — aspects to ASC and MC."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from astrologica import (
    ChartData,
    Place,
    Planet,
    compute_natal_chart,
)
from astrologica._internal.domain.aspect.angle import Angle
from astrologica._internal.domain.aspect.compute import compute_aspects

pytestmark = pytest.mark.infrastructure


def _sample_chart():
    return compute_natal_chart(
        ChartData(
            datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("America/New_York")),
            place=Place(latitude=40.7128, longitude=-74.0060),
        )
    )


def test_compute_aspects_default_excludes_angles() -> None:
    chart = _sample_chart()
    aspects = compute_aspects(chart.planets)
    for a in aspects:
        assert isinstance(a.first, Planet)
        assert isinstance(a.second, Planet)


def test_compute_aspects_with_include_angles_yields_angle_aspects() -> None:
    chart = _sample_chart()
    aspects = compute_aspects(
        chart.planets,
        include_angles=(Angle.ASCENDANT, Angle.MIDHEAVEN),
        chart=chart,
    )
    has_angle = any(isinstance(a.first, Angle) or isinstance(a.second, Angle) for a in aspects)
    assert has_angle, "expected at least one aspect to involve an angle"


def test_compute_aspects_include_angles_requires_chart() -> None:
    chart = _sample_chart()
    with pytest.raises(ValueError, match="chart"):
        compute_aspects(chart.planets, include_angles=(Angle.ASCENDANT,))
