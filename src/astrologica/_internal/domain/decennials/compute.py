"""compute_decennials — Valens' sect-conditional time-lord sequence.

Day chart: starts at the Sun and proceeds in Chaldean order from there
  → Sun (19) → Venus (8) → Mercury (20) → Moon (25) → Saturn (27) → Jupiter (12) → Mars (15).

Night chart: starts at the Moon and proceeds in Chaldean order from there
  → Moon (25) → Saturn (27) → Jupiter (12) → Mars (15) → Sun (19) → Venus (8) → Mercury (20).

Total cycle = 126 years; cycle is repeated to cover `max_age_years`.

Reference: Valens; period lengths confirmed in the friend's spec feedback.
"""

from __future__ import annotations

from astrologica._internal.domain.decennials.types import DecennialPeriod
from astrologica._internal.domain.planet.planet import Planet

_DAY_SEQUENCE: list[tuple[Planet, int]] = [
    (Planet.SUN, 19),
    (Planet.VENUS, 8),
    (Planet.MERCURY, 20),
    (Planet.MOON, 25),
    (Planet.SATURN, 27),
    (Planet.JUPITER, 12),
    (Planet.MARS, 15),
]

_NIGHT_SEQUENCE: list[tuple[Planet, int]] = [
    (Planet.MOON, 25),
    (Planet.SATURN, 27),
    (Planet.JUPITER, 12),
    (Planet.MARS, 15),
    (Planet.SUN, 19),
    (Planet.VENUS, 8),
    (Planet.MERCURY, 20),
]


def compute_decennials(
    chart: object,
    *,
    max_age_years: float = 82.0,
) -> tuple[DecennialPeriod, ...]:
    """Generate the decennial sequence for a chart, truncated at `max_age_years`.

    The cycle repeats indefinitely (period = 126 years) until accumulated age
    reaches `max_age_years`.
    """
    is_diurnal = bool(getattr(chart, "is_diurnal"))
    sequence = _DAY_SEQUENCE if is_diurnal else _NIGHT_SEQUENCE
    n = len(sequence)

    out: list[DecennialPeriod] = []
    age = 0.0
    cursor = 0
    while age < max_age_years:
        ruler, years = sequence[cursor % n]
        end = age + years
        out.append(DecennialPeriod(ruler=ruler, start_age=age, end_age=end))
        age = end
        cursor += 1
    return tuple(out)
