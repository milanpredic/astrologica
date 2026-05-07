"""compute_annual_profection — Ptolemaic 12-house annual time-lord cycle.

Year 0 (birth) activates the natal Ascendant sign and 1st house. Each
subsequent year advances by one whole sign (and one house). After 12 years
the cycle returns to the 1st house. The Lord of the Year is the domicile
ruler of the activated sign.

Reference: Ptolemy, Tetrabiblos IV.10. Algorithm shape inspired by
old_projects/morinus-console/profections.py (which computes finer-grained
monthly/daily profections via K = 365.2421904/30 days/degree); we ship the
simple annual integer-year form here.
"""

from __future__ import annotations

from astrologica._internal.domain.profection.types import ProfectionPeriod
from astrologica._internal.domain.sign import Sign
from astrologica._internal.domain.tables.rulerships import DOMICILE


def compute_annual_profection(
    chart: object,
    *,
    age_years: int,
) -> ProfectionPeriod:
    """Annual profection for a chart at integer `age_years`.

    Negative ages raise ValueError.
    """
    if age_years < 0:
        raise ValueError(f"age_years must be >= 0, got {age_years}")

    asc = float(getattr(chart, "ascendant"))
    asc_sign = Sign.of(asc)
    profected_sign_idx = (int(asc_sign) + age_years) % 12
    profected_sign = Sign(profected_sign_idx)
    profected_house = (age_years % 12) + 1
    lord_of_year = DOMICILE[profected_sign]

    return ProfectionPeriod(
        age_years=age_years,
        profected_house=profected_house,
        profected_sign=profected_sign,
        lord_of_year=lord_of_year,
    )
