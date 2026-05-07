"""planet_orientality — oriental vs occidental of the Sun."""

from __future__ import annotations

import pytest

from astrologica import Planet
from astrologica._internal.domain.measures.angle import Latitude, Longitude
from astrologica._internal.domain.measures.ecliptic import EclipticPosition, Speed
from astrologica._internal.domain.planet.position import PlanetPosition

pytestmark = pytest.mark.pure


def _pp(planet: Planet, longitude: float, speed: float = 1.0) -> PlanetPosition:
    return PlanetPosition(
        planet=planet,
        position=EclipticPosition(
            longitude=Longitude(longitude),
            latitude=Latitude(0.0),
            speed=Speed(value=speed),
        ),
    )


def test_orientality_sun_is_neutral() -> None:
    from astrologica._internal.domain.orientality.compute import Orientality, planet_orientality

    sun = _pp(Planet.SUN, 0.0)
    other = _pp(Planet.MARS, 100.0)
    planets = {Planet.SUN: sun, Planet.MARS: other}
    assert planet_orientality(Planet.SUN, planets) is Orientality.NEUTRAL


def test_orientality_moon_is_neutral() -> None:
    from astrologica._internal.domain.orientality.compute import Orientality, planet_orientality

    sun = _pp(Planet.SUN, 0.0)
    moon = _pp(Planet.MOON, 50.0)
    planets = {Planet.SUN: sun, Planet.MOON: moon}
    assert planet_orientality(Planet.MOON, planets) is Orientality.NEUTRAL


def test_orientality_planet_behind_sun_is_oriental() -> None:
    from astrologica._internal.domain.orientality.compute import Orientality, planet_orientality

    sun = _pp(Planet.SUN, 10.0)
    mars = _pp(Planet.MARS, 350.0)
    planets = {Planet.SUN: sun, Planet.MARS: mars}
    assert planet_orientality(Planet.MARS, planets) is Orientality.ORIENTAL


def test_orientality_planet_ahead_of_sun_is_occidental() -> None:
    from astrologica._internal.domain.orientality.compute import Orientality, planet_orientality

    sun = _pp(Planet.SUN, 10.0)
    mars = _pp(Planet.MARS, 30.0)
    planets = {Planet.SUN: sun, Planet.MARS: mars}
    assert planet_orientality(Planet.MARS, planets) is Orientality.OCCIDENTAL
