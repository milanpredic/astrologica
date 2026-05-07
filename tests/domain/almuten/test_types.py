"""Almuten data types — frozen, slotted, equatable."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from astrologica import Planet, Sign

pytestmark = pytest.mark.pure


def test_almuten_point_construct_and_equate() -> None:
    from astrologica._internal.domain.almuten.types import AlmutenPoint

    a = AlmutenPoint(label="Asc", longitude=171.12)
    b = AlmutenPoint(label="Asc", longitude=171.12)
    assert a == b


def test_almuten_modifiers_default_zeros() -> None:
    from astrologica._internal.domain.almuten.types import (
        DEFAULT_ALMUTEN_MODIFIERS,
        AlmutenModifiers,
    )

    assert DEFAULT_ALMUTEN_MODIFIERS == AlmutenModifiers()
    assert DEFAULT_ALMUTEN_MODIFIERS.combust == 0
    assert DEFAULT_ALMUTEN_MODIFIERS.cazimi == 0
    assert DEFAULT_ALMUTEN_MODIFIERS.angular_house == 0


def test_almuten_modifiers_frozen() -> None:
    from astrologica._internal.domain.almuten.types import AlmutenModifiers

    m = AlmutenModifiers()
    with pytest.raises(FrozenInstanceError):
        m.combust = -3  # type: ignore[misc]


def test_default_accidental_weights_zeros() -> None:
    from astrologica._internal.domain.almuten.types import DEFAULT_ACCIDENTAL_WEIGHTS
    from astrologica._internal.domain.house.quality import HouseQuality

    assert DEFAULT_ACCIDENTAL_WEIGHTS[HouseQuality.ANGULAR] == 0
    assert DEFAULT_ACCIDENTAL_WEIGHTS[HouseQuality.SUCCEDENT] == 0
    assert DEFAULT_ACCIDENTAL_WEIGHTS[HouseQuality.CADENT] == 0


def test_almuten_result_construct() -> None:
    from astrologica._internal.domain.almuten.types import (
        AlmutenPoint,
        AlmutenPointBreakdown,
        AlmutenResult,
    )

    pt = AlmutenPoint(label="Asc", longitude=0.0)
    bd = AlmutenPointBreakdown(
        point=pt,
        sign=Sign.ARIES,
        per_planet={Planet.MARS: 5},
        per_planet_text={Planet.MARS: "+5"},
    )
    result = AlmutenResult(
        winner=Planet.MARS,
        runners_up=(),
        totals={Planet.MARS: 5},
        essential_totals={Planet.MARS: 5},
        accidental_totals={Planet.MARS: 0},
        modifier_totals={Planet.MARS: 0},
        breakdown=(bd,),
        tie_break_trace=(),
    )
    assert result.winner is Planet.MARS
