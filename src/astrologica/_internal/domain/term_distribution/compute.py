"""compute_term_distribution — walk term boundaries from the natal Ascendant.

The natal Ascendant is directed forward through the zodiac at the Naibod rate
(0.98565° / year, the mean Sun's daily motion). Each term boundary the
directed point crosses ends one ruler's tenure and begins the next.

Output is a contiguous sequence of TermPeriod records covering [0, max_age_years].
"""

from __future__ import annotations

from astrologica._internal.domain.tables.terms import TermsSystem, term_boundaries
from astrologica._internal.domain.term_distribution.types import TermPeriod

_NAIBOD_DEGREES_PER_YEAR: float = 0.98565


def compute_term_distribution(
    chart: object,
    *,
    max_age_years: float = 82.0,
    terms_system: TermsSystem = TermsSystem.EGYPTIAN,
) -> tuple[TermPeriod, ...]:
    """Sequence of term-ruler periods from age 0 to `max_age_years`.

    The first period covers the time from birth until the directed Ascendant
    crosses the next term boundary; subsequent periods are full term spans
    (until the final period, which is truncated at `max_age_years`).
    """
    boundaries = term_boundaries(terms_system)
    n = len(boundaries)
    if n == 0:
        return ()

    asc = float(getattr(chart, "ascendant"))
    rate = _NAIBOD_DEGREES_PER_YEAR

    current_idx = next(
        (i for i, b in enumerate(boundaries) if b.start_longitude <= asc < b.end_longitude),
        0,
    )

    out: list[TermPeriod] = []
    age = 0.0

    first_b = boundaries[current_idx]
    span = first_b.end_longitude - asc
    end_age = min(age + span / rate, max_age_years)
    out.append(
        TermPeriod(
            start_age=age,
            end_age=end_age,
            ruler=first_b.ruler,
            sign=first_b.sign,
        )
    )
    age = end_age
    current_idx = (current_idx + 1) % n

    while age < max_age_years:
        b = boundaries[current_idx]
        span = b.end_longitude - b.start_longitude
        end_age = min(age + span / rate, max_age_years)
        out.append(
            TermPeriod(
                start_age=age,
                end_age=end_age,
                ruler=b.ruler,
                sign=b.sign,
            )
        )
        age = end_age
        current_idx = (current_idx + 1) % n

    return tuple(out)
