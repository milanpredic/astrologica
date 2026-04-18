"""Zodiacal releasing — Valens' timing technique, 4 levels, LB jump, Cap 27/30."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from astrologica.chart import compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.lot import Lot
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.sign import Sign
from astrologica.zodiacal_releasing import compute_zodiacal_releasing
from tests.fakes.fake_ephemeris import FakeEphemeris

pytestmark = pytest.mark.fake_ephemeris


@pytest.fixture
def chart():
    fake = FakeEphemeris(
        longitudes={
            Planet.SUN: 20.0,  # Aries
            Planet.MOON: 200.0,  # Libra → Fortune at Libra 10°
            Planet.MERCURY: 0.0,
            Planet.VENUS: 0.0,
            Planet.MARS: 0.0,
            Planet.JUPITER: 0.0,
            Planet.SATURN: 0.0,
        },
        ascendant=10.0,
        midheaven=280.0,
    )
    data = ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, tzinfo=UTC),
        place=Place(latitude=0.0, longitude=0.0),
    )
    return compute_natal_chart(data, ephemeris=fake)


class TestZodiacalReleasingL1:
    def test_level_1_only_produces_twelve_periods(self, chart) -> None:
        periods = compute_zodiacal_releasing(chart, lot=Lot.FORTUNE, max_level=1)
        assert len(periods) == 12
        assert all(p.level == 1 for p in periods)

    def test_level_1_starts_at_lot_sign(self, chart) -> None:
        periods = compute_zodiacal_releasing(chart, lot=Lot.FORTUNE, max_level=1)
        fortune_sign = Sign.of(float(chart.lots[Lot.FORTUNE].longitude))
        assert periods[0].sign is fortune_sign

    def test_level_1_period_durations_match_valens_table(self, chart) -> None:
        periods = compute_zodiacal_releasing(
            chart, lot=Lot.FORTUNE, max_level=1, year_length_days=360.0
        )
        expected_years = {
            Sign.ARIES: 15,
            Sign.TAURUS: 8,
            Sign.GEMINI: 20,
            Sign.CANCER: 25,
            Sign.LEO: 19,
            Sign.VIRGO: 20,
            Sign.LIBRA: 8,
            Sign.SCORPIO: 15,
            Sign.SAGITTARIUS: 12,
            Sign.CAPRICORN: 30,
            Sign.AQUARIUS: 30,
            Sign.PISCES: 12,
        }
        for p in periods:
            duration_days = (p.end - p.start).total_seconds() / 86400.0
            expected_days = expected_years[p.sign] * 360.0
            assert abs(duration_days - expected_days) < 1.0


class TestZodiacalReleasingCapricornOption:
    def test_default_capricorn_is_30(self, chart) -> None:
        periods = compute_zodiacal_releasing(chart, lot=Lot.FORTUNE, max_level=1)
        cap = next(p for p in periods if p.sign is Sign.CAPRICORN)
        days = (cap.end - cap.start).total_seconds() / 86400.0
        assert abs(days - 30 * 360.0) < 1.0

    def test_capricorn_27_option(self, chart) -> None:
        periods = compute_zodiacal_releasing(
            chart, lot=Lot.FORTUNE, max_level=1, capricorn_years=27
        )
        cap = next(p for p in periods if p.sign is Sign.CAPRICORN)
        days = (cap.end - cap.start).total_seconds() / 86400.0
        assert abs(days - 27 * 360.0) < 1.0

    def test_invalid_capricorn_years_rejected(self, chart) -> None:
        with pytest.raises(ValueError):
            compute_zodiacal_releasing(chart, lot=Lot.FORTUNE, capricorn_years=25)


class TestZodiacalReleasingL2:
    def test_level_2_sub_periods_sum_to_level_1(self, chart) -> None:
        """Sub-periods exhaustively fill each L1 period (Valens' rule)."""
        periods = compute_zodiacal_releasing(chart, lot=Lot.FORTUNE, max_level=2)
        l1 = [p for p in periods if p.level == 1]
        for parent in l1:
            children = [p for p in periods if p.level == 2 and parent.start <= p.start < parent.end]
            total_days = sum((c.end - c.start).total_seconds() for c in children) / 86400.0
            parent_days = (parent.end - parent.start).total_seconds() / 86400.0
            assert abs(total_days - parent_days) < 1.0

    def test_level_2_lb_lands_on_opposition_of_parent(self, chart) -> None:
        """When an LB fires within a parent period, the jumped-to sub-sign is
        the opposition of that *parent* sign (not the chart-level starting sign)."""
        periods = compute_zodiacal_releasing(chart, lot=Lot.FORTUNE, max_level=2)
        for p in periods:
            if not p.is_lb or p.level != 2:
                continue
            # Find the L1 parent this L2 period lives inside.
            parent = next(q for q in periods if q.level == 1 and q.start <= p.start < q.end)
            assert (p.sign.value - parent.sign.value) % 12 == 6, (
                f"LB at {p.sign.name} inside L1 parent {parent.sign.name} "
                f"should be the opposition of the parent"
            )

    def test_lb_actually_fires_for_capricorn_parent(self, chart) -> None:
        """Cap has 30y period and the Valens sub-sequence wraps within it,
        so Cap parent must produce at least one LB L2 period (jumped to Cancer)."""
        periods = compute_zodiacal_releasing(chart, lot=Lot.FORTUNE, max_level=2)
        cap_parent = next(p for p in periods if p.level == 1 and p.sign is Sign.CAPRICORN)
        cap_l2 = [
            p for p in periods if p.level == 2 and cap_parent.start <= p.start < cap_parent.end
        ]
        lb_periods = [p for p in cap_l2 if p.is_lb]
        assert len(lb_periods) >= 1
        # Cap's opposite is Cancer.
        assert all(p.sign is Sign.CANCER for p in lb_periods)


class TestZodiacalReleasingL3Plus:
    def test_level_3_subperiods_sum_to_l2(self, chart) -> None:
        periods = compute_zodiacal_releasing(chart, lot=Lot.FORTUNE, max_level=3)
        l2 = [p for p in periods if p.level == 2]
        for parent in l2:
            kids = [p for p in periods if p.level == 3 and parent.start <= p.start < parent.end]
            if not kids:
                continue
            total_days = sum((c.end - c.start).total_seconds() for c in kids) / 86400.0
            parent_days = (parent.end - parent.start).total_seconds() / 86400.0
            # Allow 1 second slack for float arithmetic.
            assert abs(total_days - parent_days) < 1.0 / 86400.0

    def test_four_levels_are_sorted_in_time(self, chart) -> None:
        periods = compute_zodiacal_releasing(chart, lot=Lot.FORTUNE, max_level=4)
        assert len(periods) > 0
        times = [p.start for p in periods]
        assert times == sorted(times)


class TestZodiacalReleasingYearLength:
    def test_tropical_year_produces_longer_calendar_durations(self, chart) -> None:
        egyptian = compute_zodiacal_releasing(
            chart, lot=Lot.FORTUNE, max_level=1, year_length_days=360.0
        )
        tropical = compute_zodiacal_releasing(
            chart, lot=Lot.FORTUNE, max_level=1, year_length_days=365.2425
        )
        for e, t in zip(egyptian, tropical, strict=True):
            e_days = (e.end - e.start).total_seconds() / 86400.0
            t_days = (t.end - t.start).total_seconds() / 86400.0
            assert t_days > e_days
            # Ratio should be 365.2425/360 regardless of sign.
            assert abs(t_days / e_days - 365.2425 / 360.0) < 1e-6


class TestZodiacalReleasingWindow:
    def test_start_and_end_clamp_output(self, chart) -> None:
        t0 = chart.data.datetime
        periods = compute_zodiacal_releasing(
            chart,
            lot=Lot.FORTUNE,
            max_level=1,
            start=t0,
            end=t0 + timedelta(days=365 * 50),  # 50 years
        )
        # No period should extend past the end bound.
        for p in periods:
            assert p.end <= t0 + timedelta(days=365 * 50) + timedelta(seconds=1)
