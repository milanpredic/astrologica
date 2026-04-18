"""Julian Day conversion correctness against known reference values."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from astrologica._internal.domain.measures.jd import julian_day

pytestmark = pytest.mark.pure


class TestJulianDay:
    def test_j2000(self) -> None:
        # J2000.0 is 2000-01-01 12:00:00 UTC, JD 2451545.0
        assert julian_day(datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)) == pytest.approx(
            2451545.0, abs=1e-6
        )

    def test_unix_epoch(self) -> None:
        # Unix epoch is JD 2440587.5
        assert julian_day(datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)) == pytest.approx(
            2440587.5, abs=1e-6
        )

    def test_converts_to_utc_before_computing(self) -> None:
        # The same moment expressed in two zones should yield the same JD.
        utc = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        tokyo = datetime(2023, 6, 15, 21, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert julian_day(utc) == pytest.approx(julian_day(tokyo), abs=1e-9)

    def test_rejects_naive_datetime(self) -> None:
        with pytest.raises(ValueError):
            julian_day(datetime(2000, 1, 1, 12, 0, 0))
