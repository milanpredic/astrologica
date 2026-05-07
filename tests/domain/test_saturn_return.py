"""compute_saturn_return — the n-th Saturn return after birth."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from astrologica import (
    ChartData,
    Place,
    Planet,
    compute_natal_chart,
    compute_saturn_return,
)

pytestmark = pytest.mark.infrastructure


def _natal():
    return compute_natal_chart(
        ChartData(
            datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("America/New_York")),
            place=Place(latitude=40.7128, longitude=-74.0060),
        )
    )


def test_saturn_return_first_is_around_age_29() -> None:
    natal = _natal()
    when = compute_saturn_return(natal, n=1)
    assert when is not None
    age_years = (when - natal.data.datetime).days / 365.25
    assert 28.5 <= age_years <= 30.5


def test_saturn_return_second_is_around_age_59() -> None:
    natal = _natal()
    when = compute_saturn_return(natal, n=2)
    assert when is not None
    age_years = (when - natal.data.datetime).days / 365.25
    assert 58.0 <= age_years <= 60.5


def test_saturn_return_n_zero_raises() -> None:
    natal = _natal()
    with pytest.raises(ValueError):
        compute_saturn_return(natal, n=0)


def test_saturn_return_lands_on_natal_saturn_longitude() -> None:
    """At the returned moment, Saturn's longitude should match natal within ~0.5°."""
    from astrologica._internal.domain.measures.jd import julian_day
    from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter

    natal = _natal()
    when = compute_saturn_return(natal, n=1)
    assert when is not None
    natal_saturn_lon = float(natal.planets[Planet.SATURN].position.longitude)
    adapter = SwissEphemerisAdapter()
    jd = julian_day(when)
    actual_lon = float(adapter.body_position(Planet.SATURN, jd).longitude)
    diff = abs(((actual_lon - natal_saturn_lon) + 180.0) % 360.0 - 180.0)
    assert diff < 0.5, f"Saturn off natal by {diff}°"
