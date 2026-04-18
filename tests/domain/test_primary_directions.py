"""Primary directions — Placidian semi-arc (zodiacal + mundane) with speculum."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica.aspect import AspectKind
from astrologica.chart import compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.primary_directions import (
    ArcKey,
    DirectionApproach,
    DirectionType,
    Speculum,
    compute_all_specula,
    compute_primary_directions,
    compute_speculum,
)
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
        place=Place(latitude=40.0, longitude=-74.0),
    )
    return compute_natal_chart(data, ephemeris=fake)


class TestPrimaryDirections:
    def test_returns_primary_direction_shape(self, chart) -> None:
        result = compute_primary_directions(chart, key=ArcKey.NAIBOD)
        assert all(hasattr(d, "promissor") and hasattr(d, "significator") for d in result)

    def test_carries_approach_field(self, chart) -> None:
        result = compute_primary_directions(chart, approach=DirectionApproach.MUNDANE)
        assert all(d.approach is DirectionApproach.MUNDANE for d in result)

    def test_default_approach_is_zodiacal(self, chart) -> None:
        result = compute_primary_directions(chart)
        assert all(d.approach is DirectionApproach.ZODIACAL for d in result)

    def test_default_aspects_are_ptolemaic(self, chart) -> None:
        result = compute_primary_directions(chart, key=ArcKey.NAIBOD)
        kinds = {d.kind for d in result}
        assert kinds <= {
            AspectKind.CONJUNCTION,
            AspectKind.SEXTILE,
            AspectKind.SQUARE,
            AspectKind.TRINE,
            AspectKind.OPPOSITION,
        }

    def test_arc_years_related_by_key(self, chart) -> None:
        """Naibod uses 0.98565°/year; Ptolemy 1°/year."""
        naibod = compute_primary_directions(chart, key=ArcKey.NAIBOD)
        ptolemy = compute_primary_directions(chart, key=ArcKey.PTOLEMY)
        for n, p in zip(naibod, ptolemy, strict=False):
            if n.arc_degrees != 0.0:
                ratio = n.years / p.years
                assert abs(ratio - (1.0 / 0.98565)) < 0.01

    def test_direct_and_converse_produce_same_count(self, chart) -> None:
        d = compute_primary_directions(chart, direction=DirectionType.DIRECT)
        c = compute_primary_directions(chart, direction=DirectionType.CONVERSE)
        assert len(d) == len(c)

    def test_all_five_arc_keys_accepted(self, chart) -> None:
        for key in ArcKey:
            result = compute_primary_directions(chart, key=key)
            assert isinstance(result, tuple)

    def test_mundane_approach_produces_distinct_arcs(self, chart) -> None:
        """Mundane and zodiacal arcs should generally disagree for
        non-conjunction aspects, confirming the two approaches are actually
        distinct computations."""
        zod = compute_primary_directions(chart, approach=DirectionApproach.ZODIACAL)
        mun = compute_primary_directions(chart, approach=DirectionApproach.MUNDANE)
        assert len(zod) == len(mun)
        # At least one pair of arcs differs — otherwise we haven't actually
        # switched algorithms.
        assert any(abs(z.arc_degrees - m.arc_degrees) > 0.1 for z, m in zip(zod, mun, strict=True))


class TestSpeculum:
    def test_speculum_has_expected_fields(self, chart) -> None:
        spec = compute_speculum(Planet.SUN, chart)
        assert isinstance(spec, Speculum)
        assert spec.body is Planet.SUN
        # All numeric fields are present and finite.
        for attr in (
            "lon",
            "lat",
            "ra",
            "decl",
            "ad_lat",
            "sa",
            "md",
            "hd",
            "th",
            "hod",
            "pmp",
            "ad_ph",
            "poh",
            "ao_do",
        ):
            v = getattr(spec, attr)
            assert isinstance(v, float)

    def test_pmp_is_in_zero_to_360(self, chart) -> None:
        for body in chart.planets:
            spec = compute_speculum(body, chart)
            assert 0.0 <= spec.pmp <= 360.0

    def test_sa_sign_matches_above_horizon(self, chart) -> None:
        for body in chart.planets:
            spec = compute_speculum(body, chart)
            if spec.is_above_horizon:
                assert spec.sa >= 0.0
            else:
                assert spec.sa <= 0.0

    def test_compute_all_specula_covers_every_body(self, chart) -> None:
        specula = compute_all_specula(chart)
        assert set(specula.keys()) == set(chart.planets.keys())

    def test_temporal_hour_is_sa_over_six(self, chart) -> None:
        for body in chart.planets:
            spec = compute_speculum(body, chart)
            assert spec.th == pytest.approx(spec.sa / 6.0, abs=1e-9)
