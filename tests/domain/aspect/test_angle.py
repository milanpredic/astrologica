"""Angle enum + Aspect endpoint widening."""

from __future__ import annotations

import pytest

from astrologica import AspectKind, Planet

pytestmark = pytest.mark.pure


def test_angle_enum_has_four_members() -> None:
    from astrologica._internal.domain.aspect.angle import Angle

    assert {a.name for a in Angle} == {"ASCENDANT", "MIDHEAVEN", "DESCENDANT", "IC"}


def test_aspect_accepts_angle_as_endpoint() -> None:
    from astrologica._internal.domain.aspect.angle import Angle
    from astrologica._internal.domain.aspect.aspect import Aspect

    a = Aspect(
        first=Angle.ASCENDANT,
        second=Planet.SUN,
        kind=AspectKind.CONJUNCTION,
        orb=1.5,
        applying=True,
    )
    assert a.first is Angle.ASCENDANT
    assert a.second is Planet.SUN


def test_aspect_planet_planet_still_works() -> None:
    from astrologica._internal.domain.aspect.aspect import Aspect

    a = Aspect(
        first=Planet.SUN,
        second=Planet.MOON,
        kind=AspectKind.CONJUNCTION,
        orb=2.0,
        applying=False,
    )
    assert a.first is Planet.SUN
