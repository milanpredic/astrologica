"""Custom lot builder — declarative DSL."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica.chart import compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.custom_lot import (
    CardinalAngle,
    CardinalAngleName,
    CustomLot,
    HouseCuspRef,
    LotFormula,
    PriorLot,
    SyzygyPoint,
    compute_custom_lot,
)
from astrologica.lot import Lot
from astrologica.place import Place
from astrologica.planet import Planet
from tests.fakes.fake_ephemeris import FakeEphemeris

pytestmark = pytest.mark.fake_ephemeris


@pytest.fixture
def chart():
    fake = FakeEphemeris(
        longitudes={
            Planet.SUN: 50.0,
            Planet.MOON: 100.0,
            Planet.MERCURY: 40.0,
            Planet.VENUS: 70.0,
            Planet.MARS: 200.0,
            Planet.JUPITER: 300.0,
            Planet.SATURN: 250.0,
        },
        speeds={p: 1.0 for p in Planet.classical()},
        ascendant=10.0,
        midheaven=280.0,
    )
    data = ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, tzinfo=UTC),
        place=Place(latitude=0.0, longitude=0.0),
    )
    return compute_natal_chart(data, ephemeris=fake)


class TestCustomLot:
    def test_rebuilt_fortune_matches_builtin(self, chart) -> None:
        """Fortune as a CustomLot → same longitude as the built-in Lot.FORTUNE."""
        fortune_custom = CustomLot(
            name="Fortune",
            day=LotFormula(plus=(Planet.MOON,), minus=(Planet.SUN,)),
            night=LotFormula(plus=(Planet.SUN,), minus=(Planet.MOON,)),
        )
        got = compute_custom_lot(chart, fortune_custom)
        expected = chart.lots[Lot.FORTUNE].longitude
        assert float(got) == pytest.approx(float(expected), abs=1e-9)

    def test_prior_lot_reference(self, chart) -> None:
        """A lot that references another lot: Nemesis = ASC + Fortune - Saturn (day)."""
        nemesis = CustomLot(
            name="Nemesis",
            day=LotFormula(plus=(PriorLot(Lot.FORTUNE),), minus=(Planet.SATURN,)),
            night=LotFormula(plus=(Planet.SATURN,), minus=(PriorLot(Lot.FORTUNE),)),
        )
        got = compute_custom_lot(chart, nemesis)
        expected = chart.lots[Lot.NEMESIS].longitude
        assert float(got) == pytest.approx(float(expected), abs=1e-9)

    def test_cardinal_angle_components(self, chart) -> None:
        """ASC + MC - Sun reachable via the DSL."""
        lot = CustomLot(
            name="asc_plus_mc_minus_sun",
            day=LotFormula(
                plus=(CardinalAngle(CardinalAngleName.MC),),
                minus=(Planet.SUN,),
            ),
            night=LotFormula(
                plus=(CardinalAngle(CardinalAngleName.MC),),
                minus=(Planet.SUN,),
            ),
        )
        got = float(compute_custom_lot(chart, lot))
        expected = (float(chart.ascendant) + float(chart.midheaven) - 50.0) % 360.0
        assert got == pytest.approx(expected, abs=1e-9)

    def test_house_cusp_ref(self, chart) -> None:
        """A lot using the 7th house cusp (= DSC)."""
        lot = CustomLot(
            name="test",
            day=LotFormula(plus=(HouseCuspRef(7),), minus=()),
            night=LotFormula(plus=(HouseCuspRef(7),), minus=()),
        )
        got = float(compute_custom_lot(chart, lot))
        expected = (float(chart.ascendant) + float(chart.houses[6].cusp)) % 360.0
        assert got == pytest.approx(expected, abs=1e-9)

    def test_syzygy_point(self, chart) -> None:
        lot = CustomLot(
            name="syzygy_test",
            day=LotFormula(plus=(SyzygyPoint(),), minus=()),
            night=LotFormula(plus=(SyzygyPoint(),), minus=()),
        )
        got = float(compute_custom_lot(chart, lot))
        expected = (float(chart.ascendant) + float(chart.syzygy.longitude)) % 360.0
        assert got == pytest.approx(expected, abs=1e-9)
