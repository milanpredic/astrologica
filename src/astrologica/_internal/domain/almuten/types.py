"""Almuten data types — input points, modifier weights, result breakdown."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from astrologica._internal.domain.house.quality import HouseQuality
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign


@dataclass(frozen=True, slots=True)
class AlmutenPoint:
    """A labeled longitude submitted as input to compute_almuten."""

    label: str
    longitude: float


@dataclass(frozen=True, slots=True)
class AlmutenModifiers:
    """Accidental and state modifier weights applied to per-planet totals.

    All fields default to zero — apps pass their preferred editorial weights.
    """

    combust: int = 0
    under_beams: int = 0
    cazimi: int = 0
    retrograde: int = 0
    aversion_to_asc: int = 0
    oriental_bonus_superior: int = 0
    occidental_bonus_inferior: int = 0
    fast_or_direct_bonus: int = 0
    angular_house: int = 0
    succedent_house: int = 0
    cadent_house: int = 0
    malefic_in_6_or_12: int = 0


DEFAULT_ALMUTEN_MODIFIERS: AlmutenModifiers = AlmutenModifiers()


DEFAULT_ACCIDENTAL_WEIGHTS: Mapping[HouseQuality, int] = {
    HouseQuality.ANGULAR: 0,
    HouseQuality.SUCCEDENT: 0,
    HouseQuality.CADENT: 0,
}


@dataclass(frozen=True, slots=True)
class AlmutenPointBreakdown:
    """Per-point essential scores for every planet."""

    point: AlmutenPoint
    sign: Sign
    per_planet: Mapping[Planet, int]
    per_planet_text: Mapping[Planet, str]


@dataclass(frozen=True, slots=True)
class AlmutenResult:
    """Almuten computation result."""

    winner: Planet | None
    runners_up: tuple[Planet, ...]
    totals: Mapping[Planet, int]
    essential_totals: Mapping[Planet, int]
    accidental_totals: Mapping[Planet, int]
    modifier_totals: Mapping[Planet, int]
    breakdown: tuple[AlmutenPointBreakdown, ...]
    tie_break_trace: tuple[str, ...]
