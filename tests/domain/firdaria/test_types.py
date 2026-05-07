"""Firdaria types and sequence tables."""

from __future__ import annotations

import pytest

from astrologica import Planet

pytestmark = pytest.mark.pure


def test_firdaria_tradition_has_two_members() -> None:
    from astrologica._internal.domain.firdaria.types import FirdariaTradition

    assert {t.name for t in FirdariaTradition} == {"AL_BIRUNI", "BONATTI"}


def test_day_sequence_starts_with_sun() -> None:
    from astrologica._internal.domain.firdaria.types import DAY_SEQUENCE

    assert DAY_SEQUENCE[0] == (Planet.SUN, 10)


def test_day_sequence_planet_years_match_traditional() -> None:
    from astrologica._internal.domain.firdaria.types import DAY_SEQUENCE

    expected = [
        (Planet.SUN, 10),
        (Planet.VENUS, 8),
        (Planet.MERCURY, 13),
        (Planet.MOON, 9),
        (Planet.SATURN, 11),
        (Planet.JUPITER, 12),
        (Planet.MARS, 7),
        (Planet.TRUE_NODE, 3),
        (Planet.SOUTH_TRUE_NODE, 2),
    ]
    assert DAY_SEQUENCE == expected


def test_albiruni_night_starts_with_moon_then_saturn() -> None:
    from astrologica._internal.domain.firdaria.types import ALBIRUNI_NIGHT_SEQUENCE

    assert ALBIRUNI_NIGHT_SEQUENCE[0] == (Planet.MOON, 9)
    assert ALBIRUNI_NIGHT_SEQUENCE[1] == (Planet.SATURN, 11)


def test_bonatti_night_has_nodes_in_middle() -> None:
    from astrologica._internal.domain.firdaria.types import BONATTI_NIGHT_SEQUENCE

    rulers = [r for r, _ in BONATTI_NIGHT_SEQUENCE]
    nn_index = rulers.index(Planet.TRUE_NODE)
    sn_index = rulers.index(Planet.SOUTH_TRUE_NODE)
    sun_index = rulers.index(Planet.SUN)
    assert nn_index < sn_index < sun_index


def test_firdaria_period_dataclass() -> None:
    from astrologica._internal.domain.firdaria.types import FirdariaPeriod, FirdariaSubPeriod

    sub = FirdariaSubPeriod(ruler=Planet.SUN, start_age=0.0, end_age=1.0)
    period = FirdariaPeriod(ruler=Planet.SUN, start_age=0.0, end_age=10.0, sub_periods=(sub,))
    assert period.ruler is Planet.SUN
    assert period.sub_periods == (sub,)
