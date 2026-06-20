"""Decennial (decennia) data types and ordered sequences.

The Valens *decennia* assign each of the seven classical planets a major
period of **10 years 9 months** (10.75y; 129 months). The sequence starts
with the sect light (Sun for diurnal, Moon for nocturnal) and proceeds in
descending Chaldean order; one full cycle of 7 planets is 75y3m (7 x 10.75).

This is distinct from the planetary-(minor-)years time-lord technique, in
which each planet rules its *own* number of years (Sun 19, Venus 8, ...);
that earlier implementation was mislabelled "decennials". See
`compute_decennials` for the corrected period system.
"""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.planet.planet import Planet

# One decennia = 10 years 9 months = 129 months.
DECENNIAL_PERIOD_YEARS: float = 10.75

# Descending Chaldean order from the sect light.
DAY_SEQUENCE: list[Planet] = [
    Planet.SUN,
    Planet.VENUS,
    Planet.MERCURY,
    Planet.MOON,
    Planet.SATURN,
    Planet.JUPITER,
    Planet.MARS,
]

NIGHT_SEQUENCE: list[Planet] = [
    Planet.MOON,
    Planet.SATURN,
    Planet.JUPITER,
    Planet.MARS,
    Planet.SUN,
    Planet.VENUS,
    Planet.MERCURY,
]


@dataclass(frozen=True, slots=True)
class DecennialSubPeriod:
    """Sub-period inside a decennia (1/7 of the major period = ~1y 6m 12d).

    The seven sub-periods walk the same Chaldean sequence forward, starting
    from the major period's own ruler.
    """

    ruler: Planet
    start_age: float
    end_age: float


@dataclass(frozen=True, slots=True)
class DecennialPeriod:
    """A major period in the Valens decennia sequence (10y9m each)."""

    ruler: Planet
    start_age: float
    end_age: float
    sub_periods: tuple[DecennialSubPeriod, ...]
