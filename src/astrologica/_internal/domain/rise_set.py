"""compute_rise_set — rise, set, MC transit, and IC transit times for a body."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from astrologica._internal.domain.measures.jd import julian_day
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.ports.ephemeris import EphemerisPort

_JD_UNIX_EPOCH = 2440587.5


def _jd_to_utc(jd_ut: float) -> datetime:
    seconds = (jd_ut - _JD_UNIX_EPOCH) * 86400.0
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)


@dataclass(frozen=True, slots=True)
class RiseSetTimes:
    """Horizon events for a body on a given day at a place.

    Any of the fields may be `None` when the event does not occur (e.g. a
    circumpolar body near the poles has no rise/set).
    """

    body: Planet
    rise: datetime | None
    mc: datetime | None
    set: datetime | None
    ic: datetime | None


def compute_rise_set(
    body: Planet,
    on: date,
    place: Place,
    ephemeris: EphemerisPort,
) -> RiseSetTimes:
    """The next rise/MC/set/IC for `body` starting from local midnight of `on`."""
    jd_midnight = julian_day(datetime(on.year, on.month, on.day, 0, 0, 0, tzinfo=UTC))

    def _opt_utc(jd: float | None) -> datetime | None:
        return None if jd is None else _jd_to_utc(jd)

    return RiseSetTimes(
        body=body,
        rise=_opt_utc(ephemeris.next_rise(body, jd_midnight - 0.1, place)),
        mc=_opt_utc(ephemeris.next_mc_transit(body, jd_midnight - 0.1, place)),
        set=_opt_utc(ephemeris.next_set(body, jd_midnight - 0.1, place)),
        ic=_opt_utc(ephemeris.next_ic_transit(body, jd_midnight - 0.1, place)),
    )
