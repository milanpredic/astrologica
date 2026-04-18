"""compute_natal_chart — orchestrator wiring with FakeEphemeris."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica.chart import ChartTradition, compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.house import HouseSystem
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.syzygy import SyzygyKind
from tests.fakes.fake_ephemeris import FakeEphemeris

pytestmark = pytest.mark.fake_ephemeris


@pytest.fixture
def fake() -> FakeEphemeris:
    """A deterministic fixture standing in for Swiss Ephemeris.

    - Sun at 50° (20° Taurus), Moon at 100° (10° Cancer).
    - Ascendant at 10°, MC at 280°.
    - Prenatal lunation: a new moon at JD=0, Moon longitude matching Sun's current.
    """
    return FakeEphemeris(
        longitudes={
            Planet.SUN: 50.0,
            Planet.MOON: 100.0,
            Planet.MERCURY: 40.0,
            Planet.VENUS: 70.0,
            Planet.MARS: 200.0,
            Planet.JUPITER: 300.0,
            Planet.SATURN: 250.0,
        },
        speeds={
            Planet.SUN: 1.0,
            Planet.MOON: 13.0,
            Planet.MERCURY: 1.2,
            Planet.VENUS: 1.1,
            Planet.MARS: 0.5,
            Planet.JUPITER: 0.08,
            Planet.SATURN: 0.03,
        },
        ascendant=10.0,
        midheaven=280.0,
        last_lunation_jd=2451545.0,
        last_lunation_moon_lon=50.0,  # same as Sun → new moon
    )


@pytest.fixture
def sample_data() -> ChartData:
    return ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=40.7128, longitude=-74.0060),
    )


class TestComputeNatalChart:
    def test_builds_chart_with_seven_planets(
        self, sample_data: ChartData, fake: FakeEphemeris
    ) -> None:
        chart = compute_natal_chart(sample_data, ephemeris=fake)
        # Default tradition is TRADITIONAL → the 7 classical bodies only.
        assert set(chart.planets.keys()) == Planet.classical()

    def test_default_tradition_is_traditional(
        self, sample_data: ChartData, fake: FakeEphemeris
    ) -> None:
        chart = compute_natal_chart(sample_data, ephemeris=fake)
        assert chart.tradition is ChartTradition.TRADITIONAL

    def test_modern_tradition_includes_outers_and_nodes(
        self, sample_data: ChartData, fake: FakeEphemeris
    ) -> None:
        chart = compute_natal_chart(sample_data, ephemeris=fake, tradition=ChartTradition.MODERN)
        assert chart.tradition is ChartTradition.MODERN
        assert set(chart.planets.keys()) == Planet.modern()
        # Outer planets and nodes are all present.
        assert Planet.URANUS in chart.planets
        assert Planet.NEPTUNE in chart.planets
        assert Planet.PLUTO in chart.planets
        assert Planet.TRUE_NODE in chart.planets
        assert Planet.MEAN_NODE in chart.planets
        assert Planet.SOUTH_TRUE_NODE in chart.planets
        assert Planet.SOUTH_MEAN_NODE in chart.planets

    def test_preserves_input(self, sample_data: ChartData, fake: FakeEphemeris) -> None:
        chart = compute_natal_chart(sample_data, ephemeris=fake)
        assert chart.data is sample_data

    def test_has_twelve_house_cusps(self, sample_data: ChartData, fake: FakeEphemeris) -> None:
        chart = compute_natal_chart(sample_data, ephemeris=fake)
        assert len(chart.houses) == 12
        # First cusp is the ascendant.
        assert float(chart.houses[0].cusp) == pytest.approx(10.0)

    def test_diurnal_determination(self, sample_data: ChartData, fake: FakeEphemeris) -> None:
        # Sun at 50°, ASC at 10° → Sun is 40° past the ASC (1st house) → NOCTURNAL.
        chart = compute_natal_chart(sample_data, ephemeris=fake)
        assert chart.is_diurnal is False

    def test_syzygy_kind_resolved(self, sample_data: ChartData, fake: FakeEphemeris) -> None:
        chart = compute_natal_chart(sample_data, ephemeris=fake)
        # FakeEphemeris reports moon at same longitude as sun → elongation 0 → NEW moon.
        assert chart.syzygy.kind is SyzygyKind.NEW_MOON

    def test_lots_are_seven(self, sample_data: ChartData, fake: FakeEphemeris) -> None:
        chart = compute_natal_chart(sample_data, ephemeris=fake)
        assert len(chart.lots) == 7

    def test_default_house_system_is_whole_sign(
        self, sample_data: ChartData, fake: FakeEphemeris
    ) -> None:
        chart = compute_natal_chart(sample_data, ephemeris=fake)
        assert chart.house_system is HouseSystem.WHOLE_SIGN

    def test_to_dict_is_json_serialisable(
        self, sample_data: ChartData, fake: FakeEphemeris
    ) -> None:
        import json

        chart = compute_natal_chart(sample_data, ephemeris=fake)
        # Round-trip through JSON — if any non-serialisable objects slip in, this raises.
        json.dumps(chart.to_dict())
