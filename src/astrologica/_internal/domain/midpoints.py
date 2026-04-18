"""compute_midpoints — 21 planet-pair midpoints among the classical 7.

A midpoint is the shortest-arc midpoint of two longitudes. For longitudes a
and b, if `|a − b| ≤ 180°` the midpoint is `(a + b) / 2`; otherwise it's
`((a + b) / 2 + 180°) mod 360°`. This guarantees the midpoint lies on the
shorter arc between the two bodies.

Midpoints of the 7 classical planets form 21 unordered pairs. Valens-style
chart work ignores outer planets and nodes for midpoints.
"""

from __future__ import annotations

from collections.abc import Mapping
from itertools import combinations

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.measures.angle import Longitude, normalize_longitude
from astrologica._internal.domain.planet.planet import Planet


def compute_midpoints(chart: Chart) -> Mapping[frozenset[Planet], Longitude]:
    """Return the 21 classical midpoints keyed by the unordered pair."""
    classical = sorted(
        (p for p in chart.planets if p.is_classical),
        key=lambda p: p.name,
    )
    result: dict[frozenset[Planet], Longitude] = {}
    for a, b in combinations(classical, 2):
        la = float(chart.planets[a].longitude)
        lb = float(chart.planets[b].longitude)
        mp = _shortest_arc_midpoint(la, lb)
        result[frozenset({a, b})] = Longitude(normalize_longitude(mp))
    return result


def _shortest_arc_midpoint(a: float, b: float) -> float:
    """Midpoint of a and b on the shorter arc, respecting wrap at 360°."""
    a = a % 360.0
    b = b % 360.0
    ccw_arc = (b - a) % 360.0  # 0 ≤ ccw_arc < 360
    if ccw_arc > 180.0:
        # Shorter arc goes clockwise from a.
        return (a + (ccw_arc - 360.0) / 2.0) % 360.0
    return (a + ccw_arc / 2.0) % 360.0
