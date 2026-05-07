"""Firdaria data types and ordered period sequences.

Sequences ported from old_projects/morinus-console/firdaria.py.
Each entry is (ruler, period_years). Nodes are included as period rulers but
have no sub-periods.

DAY_SEQUENCE: starts at Sun for diurnal charts.
ALBIRUNI_NIGHT_SEQUENCE: nocturnal Al-Biruni sequence; nodes at the end.
BONATTI_NIGHT_SEQUENCE: nocturnal Bonatti sequence; nodes mid-sequence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from astrologica._internal.domain.planet.planet import Planet


class FirdariaTradition(Enum):
    """Which Firdaria sequence to use for nocturnal charts.

    AL_BIRUNI: nodes at the end of the night sequence (most common).
    BONATTI: nodes in the middle of the night sequence (Bonatti's variant).
    The day sequence is the same in both traditions.
    """

    AL_BIRUNI = "al_biruni"
    BONATTI = "bonatti"


# (ruler, years).
DAY_SEQUENCE: list[tuple[Planet, int]] = [
    (Planet.SUN, 10),
    (Planet.VENUS, 8),
    (Planet.MERCURY, 13),
    (Planet.MOON, 9),
    (Planet.SATURN, 11),
    (Planet.JUPITER, 12),
    (Planet.MARS, 7),
    (Planet.TRUE_NODE, 3),
    (Planet.SOUTH_TRUE_NODE, 2),
]

ALBIRUNI_NIGHT_SEQUENCE: list[tuple[Planet, int]] = [
    (Planet.MOON, 9),
    (Planet.SATURN, 11),
    (Planet.JUPITER, 12),
    (Planet.MARS, 7),
    (Planet.SUN, 10),
    (Planet.VENUS, 8),
    (Planet.MERCURY, 13),
    (Planet.TRUE_NODE, 3),
    (Planet.SOUTH_TRUE_NODE, 2),
]

BONATTI_NIGHT_SEQUENCE: list[tuple[Planet, int]] = [
    (Planet.MOON, 9),
    (Planet.SATURN, 11),
    (Planet.JUPITER, 12),
    (Planet.MARS, 7),
    (Planet.TRUE_NODE, 3),
    (Planet.SOUTH_TRUE_NODE, 2),
    (Planet.SUN, 10),
    (Planet.VENUS, 8),
    (Planet.MERCURY, 13),
]


@dataclass(frozen=True, slots=True)
class FirdariaSubPeriod:
    """Sub-period inside a Firdaria period (1/7 split, six remaining planets cycle)."""

    ruler: Planet
    start_age: float
    end_age: float


@dataclass(frozen=True, slots=True)
class FirdariaPeriod:
    """A Firdaria major period.

    Node periods (TRUE_NODE / SOUTH_TRUE_NODE rulers) have no sub-periods.
    """

    ruler: Planet
    start_age: float
    end_age: float
    sub_periods: tuple[FirdariaSubPeriod, ...]
