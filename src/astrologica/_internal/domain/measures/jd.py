"""Julian Day conversion — pure math, stdlib only."""

from __future__ import annotations

from datetime import UTC, datetime


def julian_day(when: datetime) -> float:
    """Return the Julian Day (UT) for a timezone-aware datetime.

    Uses the Meeus algorithm (Astronomical Algorithms, ch. 7) valid for the full
    Gregorian era (dates after 1582-10-15).
    """
    if when.tzinfo is None:
        raise ValueError("julian_day requires a timezone-aware datetime")

    utc = when.astimezone(UTC)
    year = utc.year
    month = utc.month
    day_frac = (
        utc.day
        + (utc.hour + (utc.minute + (utc.second + utc.microsecond / 1_000_000) / 60) / 60) / 24
    )

    if month <= 2:
        year -= 1
        month += 12

    a = year // 100
    b = 2 - a + a // 4
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day_frac + b - 1524.5
