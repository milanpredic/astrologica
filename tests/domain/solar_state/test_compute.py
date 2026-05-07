"""planet_solar_state — combust / cazimi / under-beams classification."""

from __future__ import annotations

import pytest

from astrologica import Planet
from astrologica._internal.domain.measures.angle import Latitude, Longitude
from astrologica._internal.domain.measures.ecliptic import EclipticPosition, Speed
from astrologica._internal.domain.planet.position import PlanetPosition

pytestmark = pytest.mark.pure


def _pp(planet: Planet, longitude: float) -> PlanetPosition:
    return PlanetPosition(
        planet=planet,
        position=EclipticPosition(
            longitude=Longitude(longitude),
            latitude=Latitude(0.0),
            speed=Speed(value=1.0),
        ),
    )


def test_solar_state_sun_itself_is_free() -> None:
    from astrologica._internal.domain.solar_state.compute import SolarState, planet_solar_state

    sun = _pp(Planet.SUN, 0.0)
    assert planet_solar_state(sun, sun) is SolarState.FREE


def test_solar_state_within_17_arcminutes_is_cazimi() -> None:
    from astrologica._internal.domain.solar_state.compute import SolarState, planet_solar_state

    sun = _pp(Planet.SUN, 0.0)
    venus = _pp(Planet.VENUS, 0.0 + 16.0 / 60.0)
    assert planet_solar_state(venus, sun) is SolarState.CAZIMI


def test_solar_state_just_outside_cazimi_is_combust() -> None:
    from astrologica._internal.domain.solar_state.compute import SolarState, planet_solar_state

    sun = _pp(Planet.SUN, 0.0)
    venus = _pp(Planet.VENUS, 0.0 + 18.0 / 60.0)
    assert planet_solar_state(venus, sun) is SolarState.COMBUST


def test_solar_state_8d29m_is_combust() -> None:
    from astrologica._internal.domain.solar_state.compute import SolarState, planet_solar_state

    sun = _pp(Planet.SUN, 0.0)
    venus = _pp(Planet.VENUS, 8.0 + 29.0 / 60.0)
    assert planet_solar_state(venus, sun) is SolarState.COMBUST


def test_solar_state_8d30m_is_under_beams() -> None:
    from astrologica._internal.domain.solar_state.compute import SolarState, planet_solar_state

    sun = _pp(Planet.SUN, 0.0)
    venus = _pp(Planet.VENUS, 8.5)
    assert planet_solar_state(venus, sun) is SolarState.UNDER_BEAMS


def test_solar_state_17_degrees_is_free() -> None:
    from astrologica._internal.domain.solar_state.compute import SolarState, planet_solar_state

    sun = _pp(Planet.SUN, 0.0)
    venus = _pp(Planet.VENUS, 17.0)
    assert planet_solar_state(venus, sun) is SolarState.FREE


def test_solar_state_uses_shortest_arc() -> None:
    from astrologica._internal.domain.solar_state.compute import SolarState, planet_solar_state

    sun = _pp(Planet.SUN, 1.0)
    venus = _pp(Planet.VENUS, 359.0)
    assert planet_solar_state(venus, sun) is SolarState.COMBUST
