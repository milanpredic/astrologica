"""ChartConfig + chart-construction wiring of almuten/terms/per-planet state.

Verifies:
- compute_natal_chart accepts a `config` kwarg and threads terms_system into
  per-planet dignities, term_ruler, and chart.almuten_figuris.
- chart.almuten_figuris is eagerly populated using config.almuten.
- Per-planet `house`, `solar_state`, `orientality` are populated.
- Default-included aspects to ASCENDANT/MIDHEAVEN appear in chart.aspects.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica import (
    AlmutenConfig,
    AlmutenModifiers,
    ChartConfig,
    ChartData,
    ChartTradition,
    HouseQuality,
    Orientality,
    Place,
    Planet,
    SolarState,
    TermsSystem,
    compute_natal_chart,
)
from astrologica.swisseph import SwissEphemerisAdapter

pytestmark = pytest.mark.infrastructure


@pytest.fixture
def j2000() -> ChartData:
    return ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=40.0, longitude=-74.0, altitude=10.0),
    )


class TestAlmutenWired:
    def test_default_config_produces_almuten_figuris(self, j2000) -> None:
        chart = compute_natal_chart(j2000, ephemeris=SwissEphemerisAdapter())
        # Result is always present; winner may be None on dead heat but totals non-empty.
        assert chart.almuten_figuris is not None
        assert len(chart.almuten_figuris.totals) == 7  # seven classical planets

    def test_modifier_changes_almuten_score(self, j2000) -> None:
        """Adding a strong angular-house bonus should change at least one planet's total."""
        baseline = compute_natal_chart(j2000, ephemeris=SwissEphemerisAdapter())
        weighted = compute_natal_chart(
            j2000,
            ephemeris=SwissEphemerisAdapter(),
            config=ChartConfig(
                almuten=AlmutenConfig(
                    accidental_weights={
                        HouseQuality.ANGULAR: 5,
                        HouseQuality.SUCCEDENT: 2,
                        HouseQuality.CADENT: 0,
                    },
                    modifiers=AlmutenModifiers(angular_house=5),
                ),
            ),
        )
        # Totals must differ for at least one planet — the weights are non-zero
        # and the chart has classical planets in some house quality.
        diffs = {
            p: weighted.almuten_figuris.totals[p] - baseline.almuten_figuris.totals[p]
            for p in baseline.almuten_figuris.totals
        }
        assert any(d != 0 for d in diffs.values())


class TestTermsSystemThreading:
    def test_default_terms_system_is_egyptian(self, j2000) -> None:
        chart = compute_natal_chart(j2000, ephemeris=SwissEphemerisAdapter())
        assert chart.config.terms_system is TermsSystem.EGYPTIAN
        assert all(pp.terms_system is TermsSystem.EGYPTIAN for pp in chart.planets.values())

    def test_custom_terms_system_propagates_to_planet_positions(self, j2000) -> None:
        chart = compute_natal_chart(
            j2000,
            ephemeris=SwissEphemerisAdapter(),
            config=ChartConfig(terms_system=TermsSystem.PTOLEMAIC),
        )
        assert chart.config.terms_system is TermsSystem.PTOLEMAIC
        # Every PlanetPosition's term_ruler now derives from Ptolemaic.
        assert all(pp.terms_system is TermsSystem.PTOLEMAIC for pp in chart.planets.values())


class TestPerPlanetState:
    def test_house_placement_populated(self, j2000) -> None:
        chart = compute_natal_chart(j2000, ephemeris=SwissEphemerisAdapter())
        for planet, pp in chart.planets.items():
            assert pp.house is not None, f"{planet.name} has no house"
            assert 1 <= pp.house <= 12

    def test_solar_state_populated_and_sun_is_free(self, j2000) -> None:
        chart = compute_natal_chart(j2000, ephemeris=SwissEphemerisAdapter())
        for planet, pp in chart.planets.items():
            assert pp.solar_state is not None, f"{planet.name} has no solar_state"
        assert chart.planets[Planet.SUN].solar_state is SolarState.FREE

    def test_orientality_populated_and_luminaries_neutral(self, j2000) -> None:
        chart = compute_natal_chart(j2000, ephemeris=SwissEphemerisAdapter())
        for planet, pp in chart.planets.items():
            assert pp.orientality is not None, f"{planet.name} has no orientality"
        assert chart.planets[Planet.SUN].orientality is Orientality.NEUTRAL
        assert chart.planets[Planet.MOON].orientality is Orientality.NEUTRAL

    def test_non_luminaries_have_oriental_or_occidental(self, j2000) -> None:
        chart = compute_natal_chart(j2000, ephemeris=SwissEphemerisAdapter())
        non_luminary_classical = (
            Planet.MERCURY,
            Planet.VENUS,
            Planet.MARS,
            Planet.JUPITER,
            Planet.SATURN,
        )
        for planet in non_luminary_classical:
            ori = chart.planets[planet].orientality
            assert ori in (Orientality.ORIENTAL, Orientality.OCCIDENTAL)


class TestAspectsToAnglesByDefault:
    def test_chart_aspects_include_angle_endpoints(self, j2000) -> None:
        from astrologica import Angle

        chart = compute_natal_chart(j2000, ephemeris=SwissEphemerisAdapter())
        names = [
            (a.first, a.second)
            for a in chart.aspects
            if isinstance(a.first, Angle) or isinstance(a.second, Angle)
        ]
        # At least one aspect to ASC or MC across 7 classical planets is essentially guaranteed.
        assert len(names) > 0


class TestModernTraditionStillWorksWithConfig:
    def test_modern_chart_still_produces_almuten_over_classical(self, j2000) -> None:
        chart = compute_natal_chart(
            j2000,
            ephemeris=SwissEphemerisAdapter(),
            tradition=ChartTradition.MODERN,
        )
        # Almuten always operates on the 7 classical, regardless of tradition.
        assert chart.almuten_figuris is not None
        assert set(chart.almuten_figuris.totals.keys()) == {
            Planet.SUN,
            Planet.MOON,
            Planet.MERCURY,
            Planet.VENUS,
            Planet.MARS,
            Planet.JUPITER,
            Planet.SATURN,
        }
