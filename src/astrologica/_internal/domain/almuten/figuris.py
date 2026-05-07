"""compute_almuten_figuris — canonical 5-point Almuten Figuris over the hyleg points."""

from __future__ import annotations

from collections.abc import Mapping

from astrologica._internal.domain.almuten.compute import compute_almuten
from astrologica._internal.domain.almuten.types import (
    DEFAULT_ACCIDENTAL_WEIGHTS,
    DEFAULT_ALMUTEN_MODIFIERS,
    AlmutenModifiers,
    AlmutenPoint,
    AlmutenResult,
)
from astrologica._internal.domain.dignity.score import LILLY_WEIGHTS, EssentialWeights
from astrologica._internal.domain.house.quality import HouseQuality
from astrologica._internal.domain.lot.lot import Lot
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.tables.terms import TermsSystem


def compute_almuten_figuris(
    chart: object,
    *,
    essential_weights: EssentialWeights = LILLY_WEIGHTS,
    accidental_weights: Mapping[HouseQuality, int] = DEFAULT_ACCIDENTAL_WEIGHTS,
    modifiers: AlmutenModifiers = DEFAULT_ALMUTEN_MODIFIERS,
    sect_aware: bool = True,
    terms_system: TermsSystem = TermsSystem.EGYPTIAN,
) -> AlmutenResult:
    """Canonical 5-point Almuten Figuris.

    Resolves the 5 points from the chart and delegates to compute_almuten:
      - "Asc"             → chart.ascendant
      - "Sun"             → chart.planets[Planet.SUN].position.longitude
      - "Moon"            → chart.planets[Planet.MOON].position.longitude
      - "Lot of Fortune"  → chart.lots[Lot.FORTUNE].longitude
      - "Prenatal Syzygy" → chart.syzygy.longitude
    """
    planets = getattr(chart, "planets")
    lots = getattr(chart, "lots")
    syzygy = getattr(chart, "syzygy")

    points = [
        AlmutenPoint(label="Asc", longitude=float(getattr(chart, "ascendant"))),
        AlmutenPoint(label="Sun", longitude=float(planets[Planet.SUN].position.longitude)),
        AlmutenPoint(label="Moon", longitude=float(planets[Planet.MOON].position.longitude)),
        AlmutenPoint(label="Lot of Fortune", longitude=float(lots[Lot.FORTUNE].longitude)),
        AlmutenPoint(label="Prenatal Syzygy", longitude=float(syzygy.longitude)),
    ]
    return compute_almuten(
        chart,
        points=points,
        essential_weights=essential_weights,
        accidental_weights=accidental_weights,
        modifiers=modifiers,
        sect_aware=sect_aware,
        terms_system=terms_system,
    )
