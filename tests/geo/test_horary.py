"""build_horary_chart — one-liner horary from datetime-like + city."""

from __future__ import annotations

import pytest

from astrologica.chart import ChartTradition
from astrologica.geo import build_horary_chart
from astrologica.horary import HoraryChart
from astrologica.house import HouseSystem
from astrologica.planet import Planet


class TestBuildHoraryChart:
    def test_returns_horary_chart(self) -> None:
        hc = build_horary_chart("2025-06-01T12:00", "London")
        assert isinstance(hc, HoraryChart)

    def test_default_house_system_is_regiomontanus(self) -> None:
        hc = build_horary_chart("2025-06-01T12:00", "London")
        assert hc.chart.house_system is HouseSystem.REGIOMONTANUS

    def test_question_house_respected(self) -> None:
        hc = build_horary_chart("2025-06-01T12:00", "London", question_house=7)
        assert hc.question_house == 7

    def test_default_tradition_is_traditional(self) -> None:
        hc = build_horary_chart("2025-06-01T12:00", "London")
        assert hc.chart.tradition is ChartTradition.TRADITIONAL
        assert len(hc.chart.planets) == 7

    def test_modern_tradition_adds_outers_to_underlying_chart(self) -> None:
        hc = build_horary_chart("2025-06-01T12:00", "London", tradition=ChartTradition.MODERN)
        assert hc.chart.tradition is ChartTradition.MODERN
        assert Planet.URANUS in hc.chart.planets
        # Significators still come from classical rulerships.
        assert hc.significator_of_querent.is_classical
        assert hc.significator_of_quesited.is_classical

    def test_question_house_out_of_range_rejected(self) -> None:
        with pytest.raises(ValueError):
            build_horary_chart("2025-06-01T12:00", "London", question_house=13)

    def test_unknown_city_raises(self) -> None:
        with pytest.raises(LookupError):
            build_horary_chart("2025-06-01T12:00", "NotACity-xyzzy")
