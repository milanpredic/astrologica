"""Timezone resolution + build_chart_data integration."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica.chart_data import ChartData
from astrologica.geo import build_chart_data, resolve_timezone, timezone_name_for
from astrologica.place import Place


class TestTimezoneNameFor:
    def test_new_york(self) -> None:
        assert timezone_name_for(Place(40.7128, -74.0060)) == "America/New_York"

    def test_sydney(self) -> None:
        assert timezone_name_for(Place(-33.8688, 151.2093)) == "Australia/Sydney"


class TestResolveTimezone:
    def test_attaches_iana_zone_to_naive_datetime(self) -> None:
        place = Place(40.7128, -74.0060)
        naive = datetime(1990, 5, 15, 14, 30)
        result = resolve_timezone(naive, place)
        assert result.tzinfo is not None
        # 14:30 NY EDT in May = 18:30 UTC.
        assert result.astimezone(UTC) == datetime(1990, 5, 15, 18, 30, tzinfo=UTC)

    def test_rejects_already_tz_aware(self) -> None:
        with pytest.raises(ValueError):
            resolve_timezone(datetime(2000, 1, 1, tzinfo=UTC), Place(0.0, 0.0))


class TestBuildChartData:
    def test_one_line_convenience(self) -> None:
        data = build_chart_data(
            local=datetime(1990, 5, 15, 14, 30),
            place=Place(40.7128, -74.0060),
        )
        assert isinstance(data, ChartData)
        # Same UTC instant as the manually-constructed equivalent.
        assert data.utc == datetime(1990, 5, 15, 18, 30, tzinfo=UTC)
