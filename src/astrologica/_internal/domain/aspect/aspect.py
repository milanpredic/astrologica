"""Aspect — a relation between two chart points (planets or angles)."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.aspect.angle import Angle
from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.planet.planet import Planet

# Either a planet or a cardinal angle can occupy an aspect endpoint.
AspectEndpoint = Planet | Angle


@dataclass(frozen=True, slots=True)
class Aspect:
    """A Ptolemaic aspect between two chart points.

    Endpoints (`first`, `second`) may be planets or cardinal angles.
    `applying` means the faster body is still approaching exactness; `separating`
    (i.e. `not applying` and not `exact`) means it has already passed.
    `exact` is true when the orb is within a tiny numerical tolerance.
    """

    first: AspectEndpoint
    second: AspectEndpoint
    kind: AspectKind
    orb: float
    applying: bool
    exact: bool = False
