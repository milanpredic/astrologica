"""Aspect detection — pure function, no ephemeris."""

from __future__ import annotations

import pytest

from astrologica._internal.domain.measures.angle import Latitude, Longitude
from astrologica._internal.domain.measures.ecliptic import EclipticPosition, Speed
from astrologica.aspect import AspectKind, compute_aspects
from astrologica.planet import Planet, PlanetPosition

pytestmark = pytest.mark.pure


def _pp(planet: Planet, longitude: float, speed: float = 1.0) -> PlanetPosition:
    return PlanetPosition(
        planet=planet,
        position=EclipticPosition(
            longitude=Longitude(longitude),
            latitude=Latitude(0.0),
            speed=Speed(speed),
        ),
    )


class TestComputeAspects:
    def test_detects_exact_conjunction(self) -> None:
        result = compute_aspects(
            {
                Planet.SUN: _pp(Planet.SUN, 100.0, speed=1.0),
                Planet.MERCURY: _pp(Planet.MERCURY, 100.0, speed=1.0),
            }
        )
        assert len(result) == 1
        a = result[0]
        assert a.kind is AspectKind.CONJUNCTION
        assert a.orb == pytest.approx(0.0, abs=1e-6)
        assert a.exact is True

    def test_detects_trine_within_orb(self) -> None:
        # Sun at 0° Aries, Jupiter at 120° 05' — 5' orb on a trine (well within 7° default).
        result = compute_aspects(
            {
                Planet.SUN: _pp(Planet.SUN, 0.0, speed=1.0),
                Planet.JUPITER: _pp(Planet.JUPITER, 120.08, speed=0.1),
            }
        )
        assert len(result) == 1
        assert result[0].kind is AspectKind.TRINE

    def test_out_of_orb_no_aspect(self) -> None:
        # 100° apart — too wide for a square (6°) and not near any other aspect.
        result = compute_aspects(
            {
                Planet.SUN: _pp(Planet.SUN, 0.0, speed=1.0),
                Planet.MARS: _pp(Planet.MARS, 100.0, speed=0.5),
            }
        )
        assert result == ()

    def test_first_is_the_slower_body(self) -> None:
        """For an aspect between two planets, `first` is the slower, `second` the faster."""
        result = compute_aspects(
            {
                Planet.SUN: _pp(Planet.SUN, 0.0, speed=1.0),  # faster
                Planet.SATURN: _pp(Planet.SATURN, 120.0, speed=0.03),  # much slower
            }
        )
        a = result[0]
        assert a.first is Planet.SATURN
        assert a.second is Planet.SUN

    def test_detects_semisextile(self) -> None:
        """30° apart within 2° default orb → semisextile."""
        result = compute_aspects(
            {
                Planet.SUN: _pp(Planet.SUN, 0.0),
                Planet.VENUS: _pp(Planet.VENUS, 30.5),
            }
        )
        assert len(result) == 1
        assert result[0].kind is AspectKind.SEMISEXTILE

    def test_detects_quincunx(self) -> None:
        """150° apart within 2° default orb → quincunx / inconjunct."""
        result = compute_aspects(
            {
                Planet.SUN: _pp(Planet.SUN, 0.0),
                Planet.SATURN: _pp(Planet.SATURN, 150.0, speed=0.03),
            }
        )
        assert len(result) == 1
        assert result[0].kind is AspectKind.QUINCUNX

    def test_semisextile_and_quincunx_outside_tight_orb_not_detected(self) -> None:
        """Default orbs for semisextile/quincunx are 2°; 5° apart (non-luminary) → no aspect."""
        for target_angle in (30.0, 150.0):
            result = compute_aspects(
                {
                    Planet.MARS: _pp(Planet.MARS, 0.0, speed=0.5),
                    Planet.VENUS: _pp(Planet.VENUS, target_angle + 5.0, speed=1.0),
                }
            )
            assert result == (), f"unexpected aspect at {target_angle}+5°"

    def test_applying_when_faster_body_approaches(self) -> None:
        """Saturn at 0°, Moon at 110° (5° below trine) moving forward fast →
        approaching exact trine → applying."""
        result = compute_aspects(
            {
                Planet.SATURN: _pp(Planet.SATURN, 0.0, speed=0.03),
                Planet.MOON: _pp(Planet.MOON, 115.0, speed=13.0),
            }
        )
        trine = [a for a in result if a.kind is AspectKind.TRINE]
        assert len(trine) == 1
        assert trine[0].applying is True

    def test_separating_when_faster_body_has_passed_exactness(self) -> None:
        """Saturn at 0°, Moon at 125° moving forward → already past exact
        trine (120°) → separating."""
        result = compute_aspects(
            {
                Planet.SATURN: _pp(Planet.SATURN, 0.0, speed=0.03),
                Planet.MOON: _pp(Planet.MOON, 125.0, speed=13.0),
            }
        )
        trine = [a for a in result if a.kind is AspectKind.TRINE]
        assert len(trine) == 1
        assert trine[0].applying is False

    def test_at_most_one_aspect_kind_per_pair(self) -> None:
        # Exactly 180° apart — an opposition. Make sure we don't also report a
        # conjunction or square just because the orbs are loose.
        result = compute_aspects(
            {
                Planet.SUN: _pp(Planet.SUN, 0.0),
                Planet.MOON: _pp(Planet.MOON, 180.0),
            }
        )
        kinds = [a.kind for a in result]
        assert kinds == [AspectKind.OPPOSITION]
