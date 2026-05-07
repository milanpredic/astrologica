"""Aversion — the absence of any Ptolemaic aspect between two chart points.

Traditional definition: two points are in aversion if they share NO Ptolemaic
aspect (conjunction, sextile, square, trine, opposition) within default orbs.
Semisextile (30°) and quincunx (150°) do NOT count as aspects for aversion.
"""

from __future__ import annotations

from astrologica._internal.domain.aspect.angle import Angle
from astrologica._internal.domain.aspect.aspect import AspectEndpoint
from astrologica._internal.domain.aspect.compute import compute_aspects
from astrologica._internal.domain.aspect.kind import AspectKind

_PTOLEMAIC: frozenset[AspectKind] = frozenset(
    {
        AspectKind.CONJUNCTION,
        AspectKind.SEXTILE,
        AspectKind.SQUARE,
        AspectKind.TRINE,
        AspectKind.OPPOSITION,
    }
)


def is_in_aversion_to(
    point: AspectEndpoint,
    target: AspectEndpoint,
    chart: object,
) -> bool:
    """True if `point` shares no Ptolemaic aspect with `target` within default orbs."""
    if point == target:
        return False  # a point conjuncts itself

    angles_used: list[Angle] = []
    if isinstance(point, Angle):
        angles_used.append(point)
    if isinstance(target, Angle) and (point != target):
        angles_used.append(target)

    aspects = compute_aspects(
        getattr(chart, "planets"),
        include_angles=tuple(angles_used),
        chart=chart if angles_used else None,
    )
    pair = frozenset({point, target})
    for a in aspects:
        if a.kind not in _PTOLEMAIC:
            continue
        if frozenset({a.first, a.second}) == pair:
            return False
    return True
