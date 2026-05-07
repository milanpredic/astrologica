"""Profection period type."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign


@dataclass(frozen=True, slots=True)
class ProfectionPeriod:
    """Annual profection result for a given age.

    `profected_house` is the natal house number the year activates (1-12),
    where year 0 = 1st house, year 1 = 2nd house, … year 12 = 1st again.

    `profected_sign` is the zodiacal sign that house occupies under whole-sign
    profection (sign of the Ascendant, advanced by `age_years` modulo 12).

    `lord_of_year` is the domicile ruler of `profected_sign`.
    """

    age_years: int
    profected_house: int
    profected_sign: Sign
    lord_of_year: Planet
