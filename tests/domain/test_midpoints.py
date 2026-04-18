"""Midpoints — 21 classical planet-pair midpoints."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica.chart import compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.midpoints import compute_midpoints
from astrologica.place import Place
from astrologica.planet import Planet
from tests.fakes.fake_ephemeris import FakeEphemeris

pytestmark = pytest.mark.fake_ephemeris


@pytest.fixture
def chart():
    fake = FakeEphemeris(
        longitudes={
            Planet.SUN: 0.0,
            Planet.MOON: 180.0,
            Planet.MERCURY: 10.0,
            Planet.VENUS: 350.0,  # near Sun across the wrap
            Planet.MARS: 60.0,
            Planet.JUPITER: 120.0,
            Planet.SATURN: 240.0,
        },
        ascendant=10.0,
        midheaven=280.0,
    )
    data = ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=0.0, longitude=0.0),
    )
    return compute_natal_chart(data, ephemeris=fake)


class TestMidpoints:
    def test_returns_21_pairs(self, chart) -> None:
        mids = compute_midpoints(chart)
        assert len(mids) == 21  # C(7, 2)

    def test_sun_moon_opposition_midpoint_is_either_quadrature(self, chart) -> None:
        """Sun 0° and Moon 180° are exactly opposite — both 90° and 270° are
        equidistant midpoints. Either is acceptable; the library picks a
        deterministic one based on iteration order."""
        mids = compute_midpoints(chart)
        mp = float(mids[frozenset({Planet.SUN, Planet.MOON})])
        assert mp == pytest.approx(90.0, abs=1e-6) or mp == pytest.approx(270.0, abs=1e-6)

    def test_wrap_near_zero(self, chart) -> None:
        """Sun 0° and Venus 350°: the shortest arc is 10° wide; midpoint at 355°."""
        mids = compute_midpoints(chart)
        mp = float(mids[frozenset({Planet.SUN, Planet.VENUS})])
        assert mp == pytest.approx(355.0, abs=1e-6)

    def test_commutative(self, chart) -> None:
        """Keys are frozensets, so (a, b) and (b, a) land on the same entry."""
        mids = compute_midpoints(chart)
        pair1 = frozenset({Planet.MARS, Planet.JUPITER})
        pair2 = frozenset({Planet.JUPITER, Planet.MARS})
        assert pair1 == pair2
        assert mids[pair1] == mids[pair2]
