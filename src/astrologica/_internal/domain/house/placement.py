"""house_of — locate which 1..12 house a longitude falls in, given cusps."""

from __future__ import annotations

from astrologica._internal.domain.house.cusp import HouseCusp


def house_of(longitude: float, cusps: tuple[HouseCusp, ...]) -> int | None:
    """Return the 1-based house number containing `longitude`, or None.

    `cusps` must be ordered 1..12. Handles the wrap-around case where the
    12th-house cusp's "next" cusp is the 1st cusp.
    """
    norm = longitude % 360.0
    n = len(cusps)
    if n == 0:
        return None
    for i in range(n):
        a = float(cusps[i].cusp) % 360.0
        b = float(cusps[(i + 1) % n].cusp) % 360.0
        if a <= b:
            if a <= norm < b:
                return i + 1
        else:  # span wraps zero
            if norm >= a or norm < b:
                return i + 1
    return None
