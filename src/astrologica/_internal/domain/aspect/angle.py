"""Cardinal angles — Ascendant, Midheaven, and their antipodes.

These are first-class chart points (alongside planets) that can take part in
aspect relations. Treated as static for natal-snapshot semantics; their
diurnal motion is not modeled here.
"""

from __future__ import annotations

from enum import Enum


class Angle(Enum):
    """A cardinal angle of the chart."""

    ASCENDANT = "asc"
    MIDHEAVEN = "mc"
    DESCENDANT = "dsc"
    IC = "ic"
