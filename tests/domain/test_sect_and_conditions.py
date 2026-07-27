"""Sect (halb/hayz) + traditional conditions — pure functions, no ephemeris.

Validation anchors come from two worked charts of the astrohealth calibration
series: M25 (26 Aug 2025, Novi Sad — Mercury in hayz, the Moon besieged by
rays between Saturn and Mars) and M26 (7 May 2025, Belgrade — the Moon in
hayz in a night chart; Moon phase 2nd quarter).
"""

from __future__ import annotations

import pytest

from astrologica._internal.domain.measures.angle import Latitude, Longitude
from astrologica._internal.domain.measures.ecliptic import EclipticPosition, Speed
from astrologica.aspect import AspectKind, compute_aspects, lilly_moiety_orb
from astrologica.conditions import (
    MoonQuarter,
    compute_besiegement,
    compute_void_of_course,
    in_via_combusta,
    moon_phase,
)
from astrologica.planet import Planet, PlanetPosition
from astrologica.sect import PlanetSect, compute_sect_statuses

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


# M25 chart (26 Aug 2025, 15:41, Novi Sad) — day chart, Asc 24°49′ Sagittarius.
_M25 = {
    Planet.SUN: _pp(Planet.SUN, 153.6, speed=0.96),
    Planet.MOON: _pp(Planet.MOON, 192.05, speed=13.2),
    Planet.MERCURY: _pp(Planet.MERCURY, 137.5, speed=1.2),
    Planet.VENUS: _pp(Planet.VENUS, 110.0, speed=1.2),
    Planet.MARS: _pp(Planet.MARS, 192.4, speed=0.6),
    Planet.JUPITER: _pp(Planet.JUPITER, 106.9, speed=0.2),
    Planet.SATURN: _pp(Planet.SATURN, 0.38, speed=-0.05),
}
_M25_ASC = 264.8


class TestSect:
    def test_m25_mercury_in_hayz(self) -> None:
        """M25: oriental Mercury, day chart, above horizon, masculine Leo → hayz."""
        statuses = compute_sect_statuses(_M25, ascendant=_M25_ASC, is_diurnal=True)
        mercury = statuses[Planet.MERCURY]
        assert mercury.planet_sect is PlanetSect.DIURNAL  # oriental of the Sun
        assert mercury.in_sect and mercury.above_horizon
        assert mercury.in_halb and mercury.in_hayz

    def test_m26_moon_in_hayz_night_chart(self) -> None:
        """M26: night chart, Moon above horizon in feminine Virgo → hayz."""
        positions = {
            Planet.SUN: _pp(Planet.SUN, 47.5, speed=0.97),
            Planet.MOON: _pp(Planet.MOON, 174.66, speed=13.0),
            Planet.SATURN: _pp(Planet.SATURN, 358.5, speed=0.1),
        }
        statuses = compute_sect_statuses(positions, ascendant=258.1, is_diurnal=False)
        moon = statuses[Planet.MOON]
        assert moon.planet_sect is PlanetSect.NOCTURNAL
        assert moon.in_sect and moon.above_horizon
        assert moon.in_halb and moon.in_hayz

    def test_out_of_sect_diurnal_planet_below_horizon_by_day_lacks_halb(self) -> None:
        positions = {
            Planet.SUN: _pp(Planet.SUN, 100.0, speed=1.0),
            Planet.SATURN: _pp(Planet.SATURN, 120.0, speed=0.1),
        }
        # Asc 100 → Saturn at 120 has not risen → below horizon in a day chart.
        statuses = compute_sect_statuses(positions, ascendant=100.0, is_diurnal=True)
        saturn = statuses[Planet.SATURN]
        assert saturn.in_sect and not saturn.above_horizon
        assert not saturn.in_halb and not saturn.in_hayz


class TestViaCombusta:
    def test_span(self) -> None:
        assert in_via_combusta(195.0)
        assert in_via_combusta(210.0)
        assert in_via_combusta(225.0)
        assert not in_via_combusta(194.9)
        assert not in_via_combusta(225.1)
        assert not in_via_combusta(100.0)


class TestMoonPhase:
    def test_m26_second_quarter(self) -> None:
        """M26 temperament resource: 'Moon's phase is 2nd quarter'."""
        phase = moon_phase(47.5, 174.66)
        assert phase.quarter is MoonQuarter.SECOND
        assert phase.waxing

    def test_fourth_quarter_waning(self) -> None:
        phase = moon_phase(100.0, 20.0)  # elongation 280
        assert phase.quarter is MoonQuarter.FOURTH
        assert not phase.waxing


class TestBesiegement:
    def test_m25_moon_besieged_by_rays(self) -> None:
        """M25: the Moon separating ☍ Saturn, applying ☌ Mars — razapet."""
        result = compute_besiegement(_M25, Planet.MOON)
        assert result.by_rays
        assert result.separating_from is Planet.SATURN
        assert result.applying_to is Planet.MARS

    def test_bodily_enclosure_between_the_malefics(self) -> None:
        positions = {
            Planet.SUN: _pp(Planet.SUN, 300.0),
            Planet.MOON: _pp(Planet.MOON, 250.0, speed=13.0),
            Planet.MERCURY: _pp(Planet.MERCURY, 310.0),
            Planet.VENUS: _pp(Planet.VENUS, 20.0),
            Planet.MARS: _pp(Planet.MARS, 95.0, speed=0.5),
            Planet.JUPITER: _pp(Planet.JUPITER, 200.0),
            Planet.SATURN: _pp(Planet.SATURN, 105.0, speed=0.1),
        }
        target = dict(positions)
        target[Planet.VENUS] = _pp(Planet.VENUS, 100.0, speed=1.2)
        result = compute_besiegement(target, Planet.VENUS)
        assert result.bodily
        assert result.arc_to_prior == pytest.approx(5.0)
        assert result.arc_to_next == pytest.approx(5.0)

    def test_malefic_itself_is_never_besieged(self) -> None:
        result = compute_besiegement(_M25, Planet.MARS)
        assert not result.bodily and not result.by_rays


class TestVoidOfCourse:
    def test_perfection_before_sign_exit_is_not_void(self) -> None:
        positions = {
            Planet.MOON: _pp(Planet.MOON, 55.0, speed=13.0),  # 25° Taurus
            Planet.MERCURY: _pp(Planet.MERCURY, 148.0, speed=1.0),  # square from 58°
        }
        result = compute_void_of_course(positions)
        assert not result.void
        assert result.next_perfection is not None
        assert result.next_perfection.planet is Planet.MERCURY
        assert result.next_perfection.angle == pytest.approx(90.0)
        assert result.next_perfection.arc == pytest.approx(3.0)

    def test_no_perfection_in_sign_is_void(self) -> None:
        positions = {
            Planet.MOON: _pp(Planet.MOON, 59.0, speed=13.0),  # 29° Taurus
            Planet.SUN: _pp(Planet.SUN, 40.0, speed=1.0),  # no contact within 1°
        }
        result = compute_void_of_course(positions)
        assert result.void
        assert result.arc_to_sign_exit == pytest.approx(1.0)


class TestMoietyOrbs:
    def test_lilly_p127_worked_example(self) -> None:
        """CA I p.127: Venus 10° Taurus trine Saturn 18° Virgo — platick within
        the moiety sum (Saturn 5 + Venus 4 = 9; distance from exactness 8)."""
        assert lilly_moiety_orb(AspectKind.TRINE, Planet.VENUS, Planet.SATURN) == 9.0
        positions = {
            Planet.VENUS: _pp(Planet.VENUS, 40.0, speed=1.2),
            Planet.SATURN: _pp(Planet.SATURN, 168.0, speed=0.1),
        }
        with_moiety = compute_aspects(positions, orb_policy=lilly_moiety_orb)
        assert any(a.kind is AspectKind.TRINE for a in with_moiety)
        with_default = compute_aspects(positions)
        assert not any(a.kind is AspectKind.TRINE for a in with_default)

    def test_orb_is_kind_independent_for_ptolemaic_aspects(self) -> None:
        assert lilly_moiety_orb(
            AspectKind.CONJUNCTION, Planet.SUN, Planet.MOON
        ) == lilly_moiety_orb(AspectKind.OPPOSITION, Planet.SUN, Planet.MOON)

    def test_bodies_outside_the_lilly_table_carry_no_moiety(self) -> None:
        """Outer planets / nodes have no Lilly orb — only the classical
        endpoint's moiety applies (and never a KeyError on modern charts)."""
        assert lilly_moiety_orb(AspectKind.TRINE, Planet.URANUS, Planet.MOON) == 6.25
        assert lilly_moiety_orb(AspectKind.SQUARE, Planet.TRUE_NODE, Planet.PLUTO) == 0.0
        positions = {
            Planet.MOON: _pp(Planet.MOON, 40.0, speed=13.0),
            Planet.URANUS: _pp(Planet.URANUS, 165.0, speed=0.05),
        }
        with_moiety = compute_aspects(positions, orb_policy=lilly_moiety_orb)
        assert any(a.kind is AspectKind.TRINE for a in with_moiety)
