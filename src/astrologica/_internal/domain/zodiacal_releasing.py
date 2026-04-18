"""compute_zodiacal_releasing — Valens' Hellenistic timing technique.

Zodiacal releasing traces time by releasing periods from each zodiac sign in
order, starting from the sign of the Lot of Fortune (body periods) or the
Lot of Spirit (career / action periods). Each sign rules for its planetary
period of years before handing off to the next sign in zodiacal order. The
same procedure recursively subdivides each period into finer levels:

    Level 1 (major periods): years, one sign at a time
    Level 2 (minor periods): each sub-sign lasts planper[sub] *months*
                             within the parent year-period
    Level 3 (sub periods):   proportional sub-scale within Level 2
    Level 4 (sub-sub):       proportional sub-scale within Level 3

**Exhaustive fill (Valens rule):** at every level, the sub-signs exhaustively
fill the parent period — the sub-sequence does *not* stop after 12 sub-signs.
For long parent periods (e.g. 30-year Capricorn at L1) the cycle repeats
multiple times within the parent, with the LB jump applied on each repeat.

**Loosing of the Bond (LB) rule:** when the sub-sequence, cycling through
signs in zodiacal order, arrives back at the parent's starting sign, Valens
*jumps* to the opposition sign instead of repeating the start. Successive
signs continue in zodiacal order from there. The jumped period carries
`is_lb=True`.

Year length:
- `year_length_days=360.0` (default) matches Valens' Egyptian-year arithmetic.
- `year_length_days=365.2425` uses the tropical year.

Capricorn's period:
- Default 30 years.
- `capricorn_years=27` switches to the 27-year variant (alternate tradition).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.lot.lot import Lot
from astrologica._internal.domain.sign import Sign

# Valens' planetary periods per sign, in years (zodiacal order, Aries first).
_PERIOD_YEARS_DEFAULT: tuple[int, ...] = (
    15,  # Aries (Mars)
    8,  # Taurus (Venus)
    20,  # Gemini (Mercury)
    25,  # Cancer (Moon)
    19,  # Leo (Sun)
    20,  # Virgo (Mercury)
    8,  # Libra (Venus)
    15,  # Scorpio (Mars)
    12,  # Sagittarius (Jupiter)
    30,  # Capricorn (Saturn) — 27 in the alternate tradition
    30,  # Aquarius (Saturn)
    12,  # Pisces (Jupiter)
)


@dataclass(frozen=True, slots=True)
class ReleasingPeriod:
    """A single ZR period — a sign ruling an interval at a given level.

    `level` is 1..4 (major → sub-sub). `is_lb` is True for the sub-period the
    LB jump lands on (the sign in opposition to the parent's starting sign
    when the sub-sequence has returned to the parent's start). `is_peak` is
    True for periods in angular relation (conjunction / square / trine /
    opposition) to the *chart-level* starting sign.
    """

    level: int
    sign: Sign
    start: datetime
    end: datetime
    is_lb: bool
    is_peak: bool


def compute_zodiacal_releasing(
    chart: Chart,
    lot: Lot = Lot.SPIRIT,
    max_level: int = 4,
    year_length_days: float = 360.0,
    capricorn_years: int = 30,
    start: datetime | None = None,
    end: datetime | None = None,
) -> tuple[ReleasingPeriod, ...]:
    """Return the ZR periods from the given lot.

    - `lot`: FORTUNE (body periods) or SPIRIT (career / action periods).
    - `max_level`: deepest level to subdivide (1..4).
    - `year_length_days`: 360 (Valens default) or 365.2425 (tropical).
    - `capricorn_years`: 30 (default) or 27 (alternate).
    - `start` / `end`: restrict to this window. Default start is
      `chart.data.datetime`; default end is start + full Level-1 cycle total.
    """
    if max_level < 1 or max_level > 4:
        raise ValueError("max_level must be between 1 and 4")
    if capricorn_years not in (27, 30):
        raise ValueError("capricorn_years must be 27 or 30")

    period_years = list(_PERIOD_YEARS_DEFAULT)
    period_years[Sign.CAPRICORN.value] = capricorn_years
    period_table = tuple(period_years)

    lot_lon = float(chart.lots[lot].longitude)
    starting_sign = Sign.of(lot_lon)

    t0 = start if start is not None else chart.data.datetime
    if end is None:
        total_cycle_years = sum(period_table)
        t_end = t0 + timedelta(days=total_cycle_years * year_length_days)
    else:
        t_end = end

    periods: list[ReleasingPeriod] = []
    _release(
        level=1,
        parent_sign=starting_sign,
        starting_sign=starting_sign,
        parent_start=t0,
        parent_end=t_end,
        parent_years=None,  # top-level: each sign contributes its full period
        max_level=max_level,
        year_length_days=year_length_days,
        period_table=period_table,
        out=periods,
    )
    periods.sort(key=lambda p: (p.start, p.level))
    return tuple(periods)


def _release(
    level: int,
    parent_sign: Sign,
    starting_sign: Sign,
    parent_start: datetime,
    parent_end: datetime,
    parent_years: float | None,
    max_level: int,
    year_length_days: float,
    period_table: tuple[int, ...],
    out: list[ReleasingPeriod],
) -> None:
    """Emit periods at `level`, exhaustively filling the parent interval.

    - Level 1: each sign contributes its full planetary period in years; the
      loop terminates when `parent_end` is reached.
    - Levels ≥ 2: each sub-sign contributes `planper[sub]` "months-of-this-scale"
      within the parent. One "month" at Level 2 = parent_years / 12 years.

    The LB jump fires when the running sub-sequence would return to the parent
    sign — at that point the next sub-sign is the opposition of the parent.
    """
    # Valens' scale rule: one "unit" at level N equals 1/12^(N-1) years,
    # independent of parent length. At L1 a sub-sign contributes planper[sub]
    # years; at L2, planper[sub] months (planper/12 years); at L3, planper/144;
    # at L4, planper/1728. The parent's length determines *how many* sub-signs
    # fit (via exhaustive fill), not the unit size.
    unit_years = 1.0 / (12.0 ** (level - 1))

    def step_years(planper_of_sub: int) -> float:
        return planper_of_sub * unit_years

    # `parent_years` is kept for signature symmetry but no longer shapes the
    # unit — kept as None for clarity (parent_end is what bounds iteration).
    _ = parent_years

    current_idx = parent_sign.value
    current_start = parent_start
    pending_lb_flag = False

    # Safety cap: bound the inner loop to avoid pathological infinite recursion
    # (e.g., if parent_years were zero). Level 1 usually terminates via the
    # parent_end bound; sub-levels via their parent exhaustion.
    max_iterations = 2048

    for _ in range(max_iterations):
        if current_start >= parent_end:
            break

        years_this = step_years(period_table[current_idx])
        if years_this <= 0.0:
            break
        days_this = years_this * year_length_days
        current_end = min(current_start + timedelta(days=days_this), parent_end)

        sign_obj = Sign(current_idx)
        is_lb = pending_lb_flag
        pending_lb_flag = False

        out.append(
            ReleasingPeriod(
                level=level,
                sign=sign_obj,
                start=current_start,
                end=current_end,
                is_lb=is_lb,
                is_peak=_is_peak(sign_obj, starting_sign),
            )
        )

        if level < max_level and current_end > current_start:
            _release(
                level=level + 1,
                parent_sign=sign_obj,
                starting_sign=starting_sign,
                parent_start=current_start,
                parent_end=current_end,
                parent_years=years_this,
                max_level=max_level,
                year_length_days=year_length_days,
                period_table=period_table,
                out=out,
            )

        current_start = current_end

        # Determine next sub-sign. LB: if the next would be the parent starting
        # sign again (full cycle of 12), jump to the opposition instead.
        next_idx = (current_idx + 1) % 12
        if level > 1 and next_idx == parent_sign.value:
            current_idx = (parent_sign.value + 6) % 12
            pending_lb_flag = True
        else:
            current_idx = next_idx


def _is_peak(a: Sign, starting: Sign) -> bool:
    """Peak = conjunction / square / trine / opposition to the chart's starting sign."""
    return (a.value - starting.value) % 12 in {0, 3, 4, 6, 8, 9}
