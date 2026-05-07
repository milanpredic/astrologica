"""compute_natal_chart(include_nodes=...) — opt-in nodes for traditional charts."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from astrologica import (
    ChartData,
    ChartTradition,
    Place,
    Planet,
    compute_natal_chart,
)

pytestmark = pytest.mark.infrastructure


def _data():
    return ChartData(
        datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("America/New_York")),
        place=Place(latitude=40.7128, longitude=-74.0060),
    )


def test_traditional_default_no_nodes() -> None:
    chart = compute_natal_chart(_data(), tradition=ChartTradition.TRADITIONAL)
    assert Planet.TRUE_NODE not in chart.planets
    assert Planet.SOUTH_TRUE_NODE not in chart.planets


def test_traditional_with_include_nodes_has_true_nodes() -> None:
    chart = compute_natal_chart(_data(), tradition=ChartTradition.TRADITIONAL, include_nodes=True)
    assert Planet.TRUE_NODE in chart.planets
    assert Planet.SOUTH_TRUE_NODE in chart.planets


def test_modern_already_has_nodes_flag_is_noop() -> None:
    a = compute_natal_chart(_data(), tradition=ChartTradition.MODERN)
    b = compute_natal_chart(_data(), tradition=ChartTradition.MODERN, include_nodes=True)
    assert set(a.planets.keys()) == set(b.planets.keys())


def test_traditional_with_nodes_south_is_180_from_north() -> None:
    chart = compute_natal_chart(_data(), tradition=ChartTradition.TRADITIONAL, include_nodes=True)
    nn = float(chart.planets[Planet.TRUE_NODE].position.longitude)
    sn = float(chart.planets[Planet.SOUTH_TRUE_NODE].position.longitude)
    diff = (sn - nn) % 360.0
    assert abs(diff - 180.0) < 1e-3
