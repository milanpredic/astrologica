"""Public facade for primary directions (Placidian / Ptolemaic)."""

from __future__ import annotations

from collections.abc import Iterable

from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.primary_directions import (
    ArcKey,
    DirectionApproach,
    DirectionType,
    PrimaryDirection,
    Speculum,
    compute_all_specula,
    compute_speculum,
)
from astrologica._internal.domain.primary_directions.compute import (
    compute_primary_directions as _compute_primary_directions,
)

__all__ = [
    "ArcKey",
    "DirectionApproach",
    "DirectionType",
    "PrimaryDirection",
    "Speculum",
    "compute_all_specula",
    "compute_primary_directions",
    "compute_speculum",
]


def compute_primary_directions(
    chart: Chart,
    key: ArcKey = ArcKey.NAIBOD,
    direction: DirectionType = DirectionType.DIRECT,
    approach: DirectionApproach = DirectionApproach.ZODIACAL,
    aspects: Iterable[AspectKind] | None = None,
    bodies: Iterable[Planet] | None = None,
) -> tuple[PrimaryDirection, ...]:
    """Primary directions for a chart.

    - `key`: arc-to-years conversion (default Naibod).
    - `direction`: DIRECT or CONVERSE.
    - `approach`: ZODIACAL (Placidian semi-arc, default) or MUNDANE (PMP-based).
    - `aspects`: which aspect kinds to include (defaults to Ptolemaic 5).
    - `bodies`: which planets to use (defaults to classical bodies in chart).
    """
    return _compute_primary_directions(
        chart,
        key=key,
        direction=direction,
        approach=approach,
        aspects=aspects,
        bodies=bodies,
    )
