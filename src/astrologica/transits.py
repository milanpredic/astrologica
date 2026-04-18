"""Public facade for transits.

Two entry points:

- `compute_transits(natal, when)` — snapshot aspects between transiting positions
  at `when` and natal placements. Useful for "what's aspecting my chart right now".
- `find_transits(natal, start, end)` — exact transit crossings in a window. Useful
  for "when will Saturn conjoin my natal Sun".

Both inherit the natal chart's tradition / ayanamsa / frame so the two position
sets are comparable.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime

from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.transits import TransitAspect, TransitEvent
from astrologica._internal.domain.transits.compute import compute_transits as _compute_transits
from astrologica._internal.domain.transits.find import find_transits as _find_transits
from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter
from astrologica._internal.ports.ephemeris import EphemerisPort

__all__ = ["TransitAspect", "TransitEvent", "compute_transits", "find_transits"]


def compute_transits(
    natal: Chart,
    when: datetime,
    ephemeris: EphemerisPort | None = None,
    orb_policy: Callable[[AspectKind, Planet, Planet], float] | None = None,
) -> tuple[TransitAspect, ...]:
    """Snapshot: aspects from transiting positions at `when` onto `natal` placements."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_transits(natal, when, adapter, orb_policy=orb_policy)


def find_transits(
    natal: Chart,
    start: datetime,
    end: datetime,
    ephemeris: EphemerisPort | None = None,
    transiting_bodies: Iterable[Planet] | None = None,
    natal_bodies: Iterable[Planet] | None = None,
    aspects: Iterable[AspectKind] | None = None,
) -> tuple[TransitEvent, ...]:
    """Range search: every exact transit crossing in `[start, end]`."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _find_transits(
        natal,
        start,
        end,
        adapter,
        transiting_bodies=transiting_bodies,
        natal_bodies=natal_bodies,
        aspects=aspects,
    )
