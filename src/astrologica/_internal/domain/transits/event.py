"""TransitEvent — a transit detected within a time window by `find_transits`."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.planet.planet import Planet


@dataclass(frozen=True, slots=True)
class TransitEvent:
    """An exact transit crossing detected within a search window.

    `when` is the moment the aspect was exact (approx. bisected to minute
    precision). `applying_before` tells you which side of exactness the
    aspect was on just before — combined with `when`, that tells you
    ingress direction.
    """

    when: datetime
    transiting: Planet
    natal: Planet
    kind: AspectKind
    applying_before: bool
