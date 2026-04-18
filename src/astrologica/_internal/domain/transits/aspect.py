"""TransitAspect — aspect from a transiting body to a natal placement."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.planet.planet import Planet


@dataclass(frozen=True, slots=True)
class TransitAspect:
    """An aspect between a transiting (current) body and a natal body.

    `applying` is true if the transiting body is moving toward exactness;
    `exact` is true when the orb is within a tiny numerical tolerance.
    """

    transiting: Planet
    natal: Planet
    kind: AspectKind
    orb: float
    applying: bool
    exact: bool = False
