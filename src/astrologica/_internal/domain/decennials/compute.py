"""compute_decennials — Valens decennia (10y9m per planet), sect-conditional.

The decennia assign each classical planet a uniform major period of
**10 years 9 months** (10.75y; 129 months):

Day chart: starts at the Sun, descending Chaldean order
  Sun -> Venus -> Mercury -> Moon -> Saturn -> Jupiter -> Mars
Night chart: starts at the Moon, descending Chaldean order
  Moon -> Saturn -> Jupiter -> Mars -> Sun -> Venus -> Mercury

One full cycle of 7 planets = 75y3m; the cycle repeats to cover
`max_age_years`. Each major period subdivides into 7 sub-periods of
10.75/7 ~ 1.536y (~1y 6m 12d), walking the same sequence forward from
the major ruler.

Reference: Vettius Valens, *Anthology* (the distribution of the decennia);
period length 129 months. (The earlier minor-years sequence — Sun 19,
Venus 8, ... totalling 126y — was a different, mislabelled technique.)
"""

from __future__ import annotations

from astrologica._internal.domain.decennials.types import (
    DAY_SEQUENCE,
    DECENNIAL_PERIOD_YEARS,
    NIGHT_SEQUENCE,
    DecennialPeriod,
    DecennialSubPeriod,
)
from astrologica._internal.domain.planet.planet import Planet


def _build_sub_periods(
    sequence: list[Planet],
    period_index: int,
    period_start: float,
) -> tuple[DecennialSubPeriod, ...]:
    """Build the 7 sub-periods within a decennia.

    Each sub-period is 1/7 of the 10.75y major period; the cycle starts at
    the major ruler and walks the sequence forward.
    """
    sub_length = DECENNIAL_PERIOD_YEARS / 7.0
    n = len(sequence)
    out: list[DecennialSubPeriod] = []
    for i in range(7):
        ruler = sequence[(period_index + i) % n]
        start = period_start + i * sub_length
        end = start + sub_length
        out.append(DecennialSubPeriod(ruler=ruler, start_age=start, end_age=end))
    return tuple(out)


def compute_decennials(
    chart: object,
    *,
    max_age_years: float = 82.0,
) -> tuple[DecennialPeriod, ...]:
    """Generate the decennia sequence for a chart, truncated at `max_age_years`.

    Major periods are 10y9m each, emitted in sect-conditioned descending
    Chaldean order (diurnal Sun-first, nocturnal Moon-first). The cycle
    (75y3m per traversal) repeats until accumulated age reaches
    `max_age_years`. Each period carries 7 sub-periods.
    """
    is_diurnal = bool(getattr(chart, "is_diurnal"))
    sequence = DAY_SEQUENCE if is_diurnal else NIGHT_SEQUENCE
    n = len(sequence)

    out: list[DecennialPeriod] = []
    age = 0.0
    cursor = 0
    while age < max_age_years:
        ruler = sequence[cursor % n]
        end = age + DECENNIAL_PERIOD_YEARS
        out.append(
            DecennialPeriod(
                ruler=ruler,
                start_age=age,
                end_age=end,
                sub_periods=_build_sub_periods(sequence, cursor % n, age),
            )
        )
        age = end
        cursor += 1
    return tuple(out)
