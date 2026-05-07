"""compute_firdaria — generate Firdaria major periods (with sub-period split).

Ported from old_projects/morinus-console/firdaria.py:60-91. The sub-period split
reserves the first 1/7 of each major period for its own ruler, then cycles the
remaining 6/7 through the other six classical planets in sequence order. Nodes
are skipped from sub-periods and node periods have no sub-periods at all.
"""

from __future__ import annotations

from astrologica._internal.domain.firdaria.types import (
    ALBIRUNI_NIGHT_SEQUENCE,
    BONATTI_NIGHT_SEQUENCE,
    DAY_SEQUENCE,
    FirdariaPeriod,
    FirdariaSubPeriod,
    FirdariaTradition,
)
from astrologica._internal.domain.planet.planet import Planet


def _select_sequence(is_diurnal: bool, tradition: FirdariaTradition) -> list[tuple[Planet, int]]:
    if is_diurnal:
        return DAY_SEQUENCE
    if tradition is FirdariaTradition.BONATTI:
        return BONATTI_NIGHT_SEQUENCE
    return ALBIRUNI_NIGHT_SEQUENCE


def _build_sub_periods(
    sequence: list[tuple[Planet, int]],
    period_index: int,
    period_start: float,
    period_length_years: float,
) -> tuple[FirdariaSubPeriod, ...]:
    """Build the 7 sub-periods within a major planet period.

    Each sub-period is 1/7 of the major period; the cycle starts at the major
    ruler and walks the sequence forward, skipping node entries.
    """
    sub_length = period_length_years / 7.0
    out: list[FirdariaSubPeriod] = []
    n = len(sequence)
    cursor = period_index
    for i in range(7):
        while sequence[cursor][0].is_node:
            cursor = (cursor + 1) % n
        ruler, _ = sequence[cursor]
        start = period_start + i * sub_length
        end = start + sub_length
        out.append(FirdariaSubPeriod(ruler=ruler, start_age=start, end_age=end))
        cursor = (cursor + 1) % n
    return tuple(out)


def compute_firdaria(
    chart: object,
    *,
    max_age_years: float = 82.0,
    tradition: FirdariaTradition = FirdariaTradition.AL_BIRUNI,
) -> tuple[FirdariaPeriod, ...]:
    """Generate the Firdaria sequence for a chart, truncated at `max_age_years`.

    Major periods are emitted in sequence-order (diurnal Sun-first or nocturnal
    Moon-first). The cycle continues past one full traversal until the
    accumulated age reaches or exceeds `max_age_years`.

    Each non-node major period carries 7 sub-periods (1/7 each, cycling
    through the other six classical planets). Node periods have no sub-periods.
    """
    is_diurnal = bool(getattr(chart, "is_diurnal"))
    sequence = _select_sequence(is_diurnal, tradition)

    out: list[FirdariaPeriod] = []
    age = 0.0
    n = len(sequence)
    cursor = 0
    while age < max_age_years:
        ruler, years = sequence[cursor]
        end = age + years
        if ruler.is_node:
            sub_periods: tuple[FirdariaSubPeriod, ...] = ()
        else:
            sub_periods = _build_sub_periods(sequence, cursor, age, float(years))
        out.append(
            FirdariaPeriod(
                ruler=ruler,
                start_age=age,
                end_age=end,
                sub_periods=sub_periods,
            )
        )
        age = end
        cursor = (cursor + 1) % n
    return tuple(out)
