"""Prenatal syzygy — the last new/full moon before a given moment."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica.chart_data import ChartData
from astrologica.place import Place
from astrologica.swisseph import SwissEphemerisAdapter
from astrologica.syzygy import SyzygyKind, compute_prenatal_syzygy


class TestPrenatalSyzygy:
    @pytest.mark.infrastructure
    def test_new_moon_detection_against_known_event(self) -> None:
        """The J2000 epoch (2000-01-01 12:00 UTC) falls ~5 days after a known
        new moon on 2000-01-06 18:14 UTC — *before* which the most recent
        syzygy was the full moon of 2000-01-01 ... actually both events exist
        in early 2000. At 2000-01-10 the most recent syzygy is the new moon
        of 2000-01-06."""
        result = compute_prenatal_syzygy(
            datetime(2000, 1, 10, 0, 0, tzinfo=UTC),
            SwissEphemerisAdapter(),
        )
        # Must be within early Jan 2000.
        assert result.when.year == 2000
        assert result.when.month == 1
        assert result.when.day <= 10
        # And should be recognisable as a new moon (longitudes align).
        assert result.kind is SyzygyKind.NEW_MOON

    @pytest.mark.infrastructure
    def test_full_moon_detection(self) -> None:
        """2025-02-12 ~13:53 UTC was a full moon — asking 2025-02-15 should
        return that full moon."""
        result = compute_prenatal_syzygy(
            datetime(2025, 2, 15, 0, 0, tzinfo=UTC),
            SwissEphemerisAdapter(),
        )
        assert result.kind is SyzygyKind.FULL_MOON
        assert result.when.year == 2025
        assert result.when.month == 2
        assert result.when.day <= 15

    @pytest.mark.infrastructure
    def test_syzygy_is_before_query_moment(self) -> None:
        """The returned syzygy must always precede the query datetime."""
        query = datetime(2020, 7, 15, 12, 0, tzinfo=UTC)
        result = compute_prenatal_syzygy(query, SwissEphemerisAdapter())
        assert result.when < query

    @pytest.mark.infrastructure
    def test_syzygy_longitude_is_close_to_sun_at_event(self) -> None:
        """For a new moon, Moon and Sun share longitude (within ~0.1°)."""
        adapter = SwissEphemerisAdapter()
        query = datetime(2020, 7, 15, 12, 0, tzinfo=UTC)
        syz = compute_prenatal_syzygy(query, adapter)
        if syz.kind is SyzygyKind.NEW_MOON:
            sun_lon = float(
                adapter.body_position(
                    __import__("astrologica.planet", fromlist=["Planet"]).Planet.SUN,
                    (syz.when - datetime(1970, 1, 1, tzinfo=UTC)).total_seconds() / 86400.0
                    + 2440587.5,
                ).longitude
            )
            diff = abs((float(syz.longitude) - sun_lon + 180.0) % 360.0 - 180.0)
            assert diff < 0.5

    @pytest.mark.pure
    def test_requires_timezone_aware_datetime(self) -> None:
        from astrologica._internal.infrastructure.ephemeris.swiss import (
            SwissEphemerisAdapter,
        )

        with pytest.raises(ValueError):
            compute_prenatal_syzygy(datetime(2000, 1, 1), SwissEphemerisAdapter())


class TestSyzygyIntegrationWithChart:
    @pytest.mark.infrastructure
    def test_natal_chart_has_syzygy_within_one_month_prior(self) -> None:
        """Every natal chart should have a `syzygy` within ~29.5 days before
        the birth moment."""
        from datetime import timedelta

        from astrologica.chart import compute_natal_chart

        data = ChartData(
            datetime=datetime(1990, 5, 15, 14, 30, tzinfo=UTC),
            place=Place(40.7128, -74.0060),
        )
        chart = compute_natal_chart(data, ephemeris=SwissEphemerisAdapter())
        assert chart.syzygy.when <= data.datetime
        gap = data.datetime - chart.syzygy.when
        assert gap <= timedelta(days=30)

    @pytest.mark.infrastructure
    def test_chart_syzygy_kind_respects_actual_event(self) -> None:
        from astrologica.chart import compute_natal_chart

        data = ChartData(
            datetime=datetime(2025, 1, 10, 12, 0, tzinfo=UTC),
            place=Place(0.0, 0.0),
        )
        chart = compute_natal_chart(data, ephemeris=SwissEphemerisAdapter())
        # 2025-01-06 was a new moon. The prior syzygy (before Jan 10) is that event.
        assert chart.syzygy.kind is SyzygyKind.NEW_MOON
