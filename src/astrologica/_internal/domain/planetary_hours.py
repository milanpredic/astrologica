"""compute_planetary_hours — Chaldean-order planetary hours for a day.

Algorithm:
1. Find sunrise, sunset, and next sunrise for the requested local date at the
   requested place.
2. Split day arc (sunrise → sunset) and night arc (sunset → next sunrise)
   each into 12 equal unequal-hours (one twelfth of the respective arc).
3. The first day hour is ruled by the *planet of the weekday at sunrise*:
   Sun=Sunday, Moon=Monday, Mars=Tuesday, Mercury=Wednesday, Jupiter=Thursday,
   Venus=Friday, Saturn=Saturday. Subsequent hours cycle through the Chaldean
   order (Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon, then repeat).

The returned list has 24 entries: 12 day hours then 12 night hours, with
(start, end, ruler). Each hour is a `PlanetaryHour`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from astrologica._internal.domain.measures.jd import julian_day
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.ports.ephemeris import EphemerisPort

_JD_UNIX_EPOCH = 2440587.5


@dataclass(frozen=True, slots=True)
class PlanetaryHour:
    """A single planetary hour: interval + ruling planet + day/night flag."""

    start: datetime
    end: datetime
    ruler: Planet
    is_daytime: bool


# Chaldean order (slowest to fastest visible body), cycled through the hours.
_CHALDEAN_ORDER: tuple[Planet, ...] = (
    Planet.SATURN,
    Planet.JUPITER,
    Planet.MARS,
    Planet.SUN,
    Planet.VENUS,
    Planet.MERCURY,
    Planet.MOON,
)

# weekday() in Python: Monday=0 .. Sunday=6
# First-hour ruler at sunrise for each weekday.
_FIRST_HOUR_RULER_BY_WEEKDAY: dict[int, Planet] = {
    0: Planet.MOON,  # Monday
    1: Planet.MARS,  # Tuesday
    2: Planet.MERCURY,  # Wednesday
    3: Planet.JUPITER,  # Thursday
    4: Planet.VENUS,  # Friday
    5: Planet.SATURN,  # Saturday
    6: Planet.SUN,  # Sunday
}


def _jd_to_utc(jd_ut: float) -> datetime:
    seconds = (jd_ut - _JD_UNIX_EPOCH) * 86400.0
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)


def compute_planetary_hours(
    on: date,
    place: Place,
    ephemeris: EphemerisPort,
) -> tuple[PlanetaryHour, ...]:
    """Return the 24 planetary hours for the local day `on` at `place`.

    The 12 day hours run sunrise → sunset and the 12 night hours run
    sunset → next sunrise. Hour durations differ between day and night, and
    vary across the year — classical "unequal hours".

    Raises `ValueError` if the Sun is circumpolar (no rise/set) at the given
    place and date — at high latitudes the concept of planetary hours does
    not apply.
    """
    # Start searching from the local date's 00:00 UTC approximation.
    jd_midnight = julian_day(datetime(on.year, on.month, on.day, 0, 0, 0, tzinfo=UTC))

    sunrise_jd = ephemeris.next_rise(Planet.SUN, jd_midnight - 0.1, place)
    if sunrise_jd is None:
        raise ValueError(f"Sun is circumpolar at {place} on {on} — planetary hours are undefined")
    sunset_jd = ephemeris.next_set(Planet.SUN, sunrise_jd, place)
    if sunset_jd is None:
        raise ValueError(f"Sun does not set at {place} on {on} — planetary hours are undefined")
    next_sunrise_jd = ephemeris.next_rise(Planet.SUN, sunset_jd, place)
    if next_sunrise_jd is None:
        raise ValueError(
            f"Sun does not rise the day after {on} at {place} — planetary hours undefined"
        )

    day_length = sunset_jd - sunrise_jd  # in days
    night_length = next_sunrise_jd - sunset_jd
    day_hour = day_length / 12.0
    night_hour = night_length / 12.0

    # Determine first-hour ruler from the weekday at sunrise (UTC).
    sunrise_utc = _jd_to_utc(sunrise_jd)
    weekday = sunrise_utc.weekday()
    first_ruler = _FIRST_HOUR_RULER_BY_WEEKDAY[weekday]
    start_idx = _CHALDEAN_ORDER.index(first_ruler)

    hours: list[PlanetaryHour] = []
    for i in range(12):
        ruler = _CHALDEAN_ORDER[(start_idx + i) % 7]
        start_jd = sunrise_jd + i * day_hour
        end_jd = sunrise_jd + (i + 1) * day_hour
        hours.append(
            PlanetaryHour(
                start=_jd_to_utc(start_jd),
                end=_jd_to_utc(end_jd),
                ruler=ruler,
                is_daytime=True,
            )
        )

    # Night hours continue the cycle (12 day hours later we're 12 steps into Chaldean).
    night_start_idx = (start_idx + 12) % 7
    for i in range(12):
        ruler = _CHALDEAN_ORDER[(night_start_idx + i) % 7]
        start_jd = sunset_jd + i * night_hour
        end_jd = sunset_jd + (i + 1) * night_hour
        hours.append(
            PlanetaryHour(
                start=_jd_to_utc(start_jd),
                end=_jd_to_utc(end_jd),
                ruler=ruler,
                is_daytime=False,
            )
        )

    return tuple(hours)
