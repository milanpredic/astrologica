"""compute_is_diurnal — day/night chart determination (traditional 'sect').

A chart is **diurnal** (day) when the Sun is above the horizon, i.e. in houses 7..12.
Equivalently in pure longitude terms: a chart is diurnal when the Sun's longitude is
in the semicircle from the descendant (ASC+180°) through the MC to the ascendant,
measured in the direction of primary motion.
"""

from __future__ import annotations


def compute_is_diurnal(sun_longitude: float, ascendant: float) -> bool:
    """Return True when the Sun is above the horizon (day chart).

    `sun_longitude` and `ascendant` are in decimal degrees; any values outside
    [0, 360) are reduced modulo 360. The Sun is above the horizon when it sits
    between the Descendant (ASC+180°) and the Ascendant going *forward* through
    the MC — which is simply the semicircle where ``(lon - asc) mod 360 >= 180``.
    """
    return ((sun_longitude - ascendant) % 360.0) >= 180.0
