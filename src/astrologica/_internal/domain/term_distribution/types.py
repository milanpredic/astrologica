"""Term-distribution period type."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign


@dataclass(frozen=True, slots=True)
class TermPeriod:
    """A span of life ruled by a single term-ruler under primary direction.

    Periods are emitted in order, contiguous, with `end_age` of one matching
    `start_age` of the next.
    """

    start_age: float
    end_age: float
    ruler: Planet
    sign: Sign
