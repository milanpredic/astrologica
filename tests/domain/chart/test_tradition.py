"""ChartTradition — TRADITIONAL vs MODERN body-set selector."""

from __future__ import annotations

from astrologica._internal.domain.chart.tradition import ChartTradition
from astrologica._internal.domain.planet.planet import Planet


class TestChartTradition:
    def test_has_traditional_and_modern_members(self) -> None:
        assert ChartTradition.TRADITIONAL is not ChartTradition.MODERN

    def test_traditional_bodies_are_the_seven_classical(self) -> None:
        assert ChartTradition.TRADITIONAL.bodies() == Planet.classical()

    def test_modern_bodies_are_the_fourteen(self) -> None:
        assert ChartTradition.MODERN.bodies() == Planet.modern()
