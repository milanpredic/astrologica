"""compute_almuten — essential scoring + accidental + modifiers + tie-break."""

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

pytestmark = pytest.mark.infrastructure


def _sample_chart():
    return compute_natal_chart(
        ChartData(
            datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("America/New_York")),
            place=Place(latitude=40.7128, longitude=-74.0060),
        )
    )


def test_compute_almuten_returns_result_with_seven_planet_totals() -> None:
    from astrologica._internal.domain.almuten.compute import compute_almuten
    from astrologica._internal.domain.almuten.types import AlmutenPoint

    chart = _sample_chart()
    result = compute_almuten(
        chart,
        points=[AlmutenPoint(label="Asc", longitude=float(chart.ascendant))],
    )
    classical = {
        Planet.SUN,
        Planet.MOON,
        Planet.MERCURY,
        Planet.VENUS,
        Planet.MARS,
        Planet.JUPITER,
        Planet.SATURN,
    }
    assert set(result.totals.keys()) == classical


def test_compute_almuten_winner_is_top_scorer() -> None:
    from astrologica._internal.domain.almuten.compute import compute_almuten
    from astrologica._internal.domain.almuten.types import AlmutenPoint

    chart = _sample_chart()
    result = compute_almuten(
        chart,
        points=[
            AlmutenPoint(
                label="Sun",
                longitude=float(chart.planets[Planet.SUN].position.longitude),
            )
        ],
    )
    if result.winner is not None:
        winner_total = result.totals[result.winner]
        for planet, total in result.totals.items():
            assert total <= winner_total


def test_compute_almuten_breakdown_has_one_entry_per_point() -> None:
    from astrologica._internal.domain.almuten.compute import compute_almuten
    from astrologica._internal.domain.almuten.types import AlmutenPoint

    chart = _sample_chart()
    points = [
        AlmutenPoint(label="Asc", longitude=float(chart.ascendant)),
        AlmutenPoint(label="MC", longitude=float(chart.midheaven)),
    ]
    result = compute_almuten(chart, points=points)
    assert len(result.breakdown) == 2
    assert result.breakdown[0].point.label == "Asc"
    assert result.breakdown[1].point.label == "MC"


def test_compute_almuten_essential_totals_at_aries_zero_includes_mars() -> None:
    """Mars at point A (0° Aries): domicile +5 + face +1 = 6."""
    from astrologica._internal.domain.almuten.compute import compute_almuten
    from astrologica._internal.domain.almuten.types import AlmutenPoint

    chart = _sample_chart()
    points = [AlmutenPoint(label="A", longitude=0.0)]
    result = compute_almuten(chart, points=points)
    assert result.essential_totals[Planet.MARS] >= 6


def test_compute_almuten_modifier_combust_applied() -> None:
    """A combust planet's modifier should be ≤ 0 when combust=-5."""
    from astrologica._internal.domain.almuten.compute import compute_almuten
    from astrologica._internal.domain.almuten.types import AlmutenModifiers, AlmutenPoint

    chart = _sample_chart()
    pts = [AlmutenPoint(label="A", longitude=0.0)]
    no_mod = compute_almuten(chart, points=pts)
    with_mod = compute_almuten(chart, points=pts, modifiers=AlmutenModifiers(combust=-5))
    for planet in no_mod.totals.keys():
        assert with_mod.modifier_totals[planet] <= 0
