"""Aspect — a relation between two planetary positions."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.planet.planet import Planet


@dataclass(frozen=True, slots=True)
class Aspect:
    """A Ptolemaic aspect between two planets in a chart.

    `applying` means the faster body is still approaching exactness; `separating`
    (i.e. `not applying` and not `exact`) means it has already passed.
    `exact` is true when the orb is within a tiny numerical tolerance.
    """

    first: Planet
    second: Planet
    kind: AspectKind
    orb: float
    applying: bool
    exact: bool = False
