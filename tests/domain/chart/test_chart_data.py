"""ChartData value object — invariants and conversions."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from astrologica.chart_data import ChartData
from astrologica.place import Place

pytestmark = pytest.mark.pure


class TestChartData:
    def test_rejects_naive_datetime(self) -> None:
        with pytest.raises(ValueError):
            ChartData(
                datetime=datetime(1990, 5, 15, 14, 30),
                place=Place(40.7, -74.0),
            )

    def test_preserves_original_tz(self) -> None:
        ny = ZoneInfo("America/New_York")
        data = ChartData(
            datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ny),
            place=Place(40.7, -74.0),
        )
        # The original tz is preserved (we don't silently convert to UTC).
        assert data.datetime.tzinfo is ny

    def test_utc_property_converts(self) -> None:
        data = ChartData(
            datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("America/New_York")),
            place=Place(40.7, -74.0),
        )
        # NY EDT is UTC-4 in May → 18:30 UTC.
        assert data.utc == datetime(1990, 5, 15, 18, 30, tzinfo=UTC)

    def test_jd_property(self) -> None:
        data = ChartData(
            datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
            place=Place(0.0, 0.0),
        )
        assert data.jd == pytest.approx(2451545.0, abs=1e-6)

    def test_from_iso(self) -> None:
        data = ChartData.from_iso("1990-05-15T14:30:00-04:00", place=Place(40.7, -74.0))
        assert data.datetime.year == 1990
        assert data.datetime.month == 5
        assert data.utc == datetime(1990, 5, 15, 18, 30, tzinfo=UTC)

    def test_is_frozen(self) -> None:
        data = ChartData(
            datetime=datetime(2020, 1, 1, tzinfo=UTC),
            place=Place(0.0, 0.0),
        )
        with pytest.raises(Exception):  # noqa: B017 — frozen dataclasses raise FrozenInstanceError
            data.place = Place(10.0, 10.0)  # type: ignore[misc]
