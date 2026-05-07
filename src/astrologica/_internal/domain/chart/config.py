"""ChartConfig — editorial knobs for chart computation.

Single configuration bundle threaded through compute_natal_chart. All fields
have sensible Hellenistic defaults so callers can ignore it. Sub-configs group
related knobs (almuten weights and modifiers); scalar settings (terms_system)
sit at the top.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from astrologica._internal.domain.almuten.types import (
    DEFAULT_ACCIDENTAL_WEIGHTS,
    DEFAULT_ALMUTEN_MODIFIERS,
    AlmutenModifiers,
)
from astrologica._internal.domain.dignity.score import LILLY_WEIGHTS, EssentialWeights
from astrologica._internal.domain.house.quality import HouseQuality
from astrologica._internal.domain.tables.terms import TermsSystem


@dataclass(frozen=True, slots=True)
class AlmutenConfig:
    """Almuten-Figuris scoring knobs.

    Defaults reproduce a standard Lilly-style reading: domicile/exaltation/
    triplicity/term/face = 5/4/3/2/1, no accidental house weighting, no
    state modifiers. Override any subset to suit a different editorial scheme.
    """

    essential_weights: EssentialWeights = LILLY_WEIGHTS
    accidental_weights: Mapping[HouseQuality, int] = field(
        default_factory=lambda: dict(DEFAULT_ACCIDENTAL_WEIGHTS)
    )
    modifiers: AlmutenModifiers = DEFAULT_ALMUTEN_MODIFIERS
    sect_aware: bool = True


DEFAULT_ALMUTEN_CONFIG: AlmutenConfig = AlmutenConfig()


@dataclass(frozen=True, slots=True)
class ChartConfig:
    """Editorial knobs for chart computation.

    `terms_system` drives every dignity-aware computation in the chart:
    each planet's dignities, its `term_ruler`, and the almuten figuris.
    Defaults to Egyptian — the Hellenistic standard.

    `almuten` bundles the five Almuten-Figuris knobs. The chart eagerly
    computes `chart.almuten_figuris` using this configuration.
    """

    terms_system: TermsSystem = TermsSystem.EGYPTIAN
    almuten: AlmutenConfig = field(default_factory=AlmutenConfig)


DEFAULT_CHART_CONFIG: ChartConfig = ChartConfig()
