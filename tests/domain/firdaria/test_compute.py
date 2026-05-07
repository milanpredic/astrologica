"""compute_firdaria — generates major periods and sub-period splits."""

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


def _diurnal_chart():
    return compute_natal_chart(
        ChartData(
            datetime=datetime(1990, 5, 15, 12, 0, tzinfo=ZoneInfo("America/New_York")),
            place=Place(latitude=40.7128, longitude=-74.0060),
        )
    )


def _nocturnal_chart():
    return compute_natal_chart(
        ChartData(
            datetime=datetime(1990, 5, 15, 0, 0, tzinfo=ZoneInfo("America/New_York")),
            place=Place(latitude=40.7128, longitude=-74.0060),
        )
    )


def test_firdaria_diurnal_first_period_is_sun() -> None:
    from astrologica._internal.domain.firdaria.compute import compute_firdaria

    chart = _diurnal_chart()
    periods = compute_firdaria(chart)
    assert periods[0].ruler is Planet.SUN
    assert periods[0].start_age == 0.0
    assert periods[0].end_age == 10.0


def test_firdaria_diurnal_total_span_reaches_max_age() -> None:
    from astrologica._internal.domain.firdaria.compute import compute_firdaria

    chart = _diurnal_chart()
    periods = compute_firdaria(chart, max_age_years=82.0)
    assert periods[0].start_age == 0.0
    assert any(p.start_age <= 82.0 <= p.end_age for p in periods)


def test_firdaria_diurnal_subperiods_count_seven_for_planet_periods() -> None:
    from astrologica._internal.domain.firdaria.compute import compute_firdaria

    chart = _diurnal_chart()
    periods = compute_firdaria(chart)
    for p in periods:
        if p.ruler.is_node:
            assert p.sub_periods == ()
        else:
            assert len(p.sub_periods) == 7


def test_firdaria_diurnal_first_subperiod_is_period_ruler() -> None:
    from astrologica._internal.domain.firdaria.compute import compute_firdaria

    chart = _diurnal_chart()
    periods = compute_firdaria(chart)
    sun_period = periods[0]
    assert sun_period.sub_periods[0].ruler is Planet.SUN


def test_firdaria_subperiod_lengths_sum_to_period_length() -> None:
    from astrologica._internal.domain.firdaria.compute import compute_firdaria

    chart = _diurnal_chart()
    periods = compute_firdaria(chart)
    sun_period = periods[0]
    total = sum(s.end_age - s.start_age for s in sun_period.sub_periods)
    assert total == pytest.approx(sun_period.end_age - sun_period.start_age)


def test_firdaria_nocturnal_first_period_is_moon() -> None:
    from astrologica._internal.domain.firdaria.compute import compute_firdaria

    chart = _nocturnal_chart()
    periods = compute_firdaria(chart)
    assert periods[0].ruler is Planet.MOON


def test_firdaria_bonatti_night_node_periods_before_sun() -> None:
    from astrologica._internal.domain.firdaria.compute import compute_firdaria
    from astrologica._internal.domain.firdaria.types import FirdariaTradition

    chart = _nocturnal_chart()
    periods = compute_firdaria(chart, tradition=FirdariaTradition.BONATTI)
    rulers = [p.ruler for p in periods]
    nn_idx = rulers.index(Planet.TRUE_NODE)
    sun_idx = rulers.index(Planet.SUN)
    assert nn_idx < sun_idx
