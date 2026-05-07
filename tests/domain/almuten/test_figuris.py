"""compute_almuten_figuris — canonical 5-point Almuten Figuris."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from astrologica import (
    ChartData,
    Lot,
    Place,
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


def test_almuten_figuris_uses_five_canonical_points() -> None:
    from astrologica._internal.domain.almuten.figuris import compute_almuten_figuris

    chart = _sample_chart()
    result = compute_almuten_figuris(chart)
    labels = [b.point.label for b in result.breakdown]
    assert labels == ["Asc", "Sun", "Moon", "Lot of Fortune", "Prenatal Syzygy"]


def test_almuten_figuris_longitudes_match_chart() -> None:
    from astrologica import Planet
    from astrologica._internal.domain.almuten.figuris import compute_almuten_figuris

    chart = _sample_chart()
    result = compute_almuten_figuris(chart)
    pts = {b.point.label: b.point.longitude for b in result.breakdown}
    assert pts["Asc"] == pytest.approx(float(chart.ascendant))
    assert pts["Sun"] == pytest.approx(float(chart.planets[Planet.SUN].position.longitude))
    assert pts["Moon"] == pytest.approx(float(chart.planets[Planet.MOON].position.longitude))
    assert pts["Lot of Fortune"] == pytest.approx(float(chart.lots[Lot.FORTUNE].longitude))
    assert pts["Prenatal Syzygy"] == pytest.approx(float(chart.syzygy.longitude))
