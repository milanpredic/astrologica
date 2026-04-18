"""build_natal_chart — end-to-end one-liner across all supported input shapes."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from astrologica.chart import Chart, ChartTradition
from astrologica.geo import build_natal_chart
from astrologica.planet import Planet


class TestBuildNatalChart:
    # ── string inputs ──────────────────────────────────────────────────────────

    def test_iso_naive_auto_resolves_tz(self) -> None:
        chart = build_natal_chart("1990-05-15T14:30", "New York")
        assert isinstance(chart, Chart)
        assert chart.planets[Planet.SUN].sign.name == "TAURUS"

    def test_iso_with_offset(self) -> None:
        chart = build_natal_chart("1990-05-15T14:30:00-04:00", "New York")
        assert chart.planets[Planet.SUN].sign.name == "TAURUS"

    # ── numeric (Unix timestamp) inputs ────────────────────────────────────────

    def test_unix_timestamp_seconds(self) -> None:
        # 1990-05-15T18:30:00Z == 642796200 seconds since epoch.
        ts = datetime(1990, 5, 15, 18, 30, tzinfo=UTC).timestamp()
        chart = build_natal_chart(ts, "New York")
        # Same instant as the ISO-with-offset case above.
        chart_iso = build_natal_chart("1990-05-15T14:30:00-04:00", "New York")
        assert chart.planets[Planet.SUN].longitude == chart_iso.planets[Planet.SUN].longitude

    def test_unix_timestamp_int(self) -> None:
        chart = build_natal_chart(642796200, "New York")
        assert chart.planets[Planet.SUN].sign.name == "TAURUS"

    # ── datetime-object inputs ─────────────────────────────────────────────────

    def test_tz_aware_datetime(self) -> None:
        dt = datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("America/New_York"))
        chart = build_natal_chart(dt, "New York")
        assert chart.planets[Planet.SUN].sign.name == "TAURUS"

    def test_naive_datetime_resolves_against_city(self) -> None:
        dt = datetime(1990, 5, 15, 14, 30)  # naive
        chart = build_natal_chart(dt, "New York")
        # 14:30 NY EDT == 18:30 UTC.
        assert chart.data.utc == datetime(1990, 5, 15, 18, 30, tzinfo=UTC)

    # ── tradition parameter ────────────────────────────────────────────────────

    def test_default_tradition_is_traditional(self) -> None:
        chart = build_natal_chart("1990-05-15T14:30", "New York")
        assert chart.tradition is ChartTradition.TRADITIONAL
        assert len(chart.planets) == 7

    def test_modern_tradition_includes_outers_and_nodes(self) -> None:
        chart = build_natal_chart("1990-05-15T14:30", "New York", tradition=ChartTradition.MODERN)
        assert chart.tradition is ChartTradition.MODERN
        assert Planet.URANUS in chart.planets
        assert Planet.NEPTUNE in chart.planets
        assert Planet.PLUTO in chart.planets
        assert Planet.TRUE_NODE in chart.planets
        assert len(chart.planets) == 14

    # ── error paths ────────────────────────────────────────────────────────────

    def test_unknown_city_raises(self) -> None:
        with pytest.raises(LookupError):
            build_natal_chart("1990-05-15T14:30", "NotACity-xyzzy")

    def test_invalid_iso_string_raises(self) -> None:
        with pytest.raises(ValueError):
            build_natal_chart("not a date", "New York")

    def test_bool_is_rejected(self) -> None:
        """`bool` is technically an int — explicitly rejected to avoid nonsense."""
        with pytest.raises(TypeError):
            build_natal_chart(True, "New York")  # type: ignore[arg-type]

    def test_unsupported_type_raises(self) -> None:
        with pytest.raises(TypeError):
            build_natal_chart(object(), "New York")  # type: ignore[arg-type]
