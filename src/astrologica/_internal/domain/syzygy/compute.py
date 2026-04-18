"""compute_prenatal_syzygy — the last new or full moon before a given moment."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from astrologica._internal.domain.ayanamsa import Ayanamsa
from astrologica._internal.domain.measures.angle import Longitude, normalize_longitude
from astrologica._internal.domain.measures.jd import julian_day
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.syzygy.kind import SyzygyKind
from astrologica._internal.domain.syzygy.syzygy import Syzygy
from astrologica._internal.ports.ephemeris import EphemerisPort


def compute_prenatal_syzygy(
    when: datetime,
    ephemeris: EphemerisPort,
    ayanamsa: Ayanamsa | None = None,
) -> Syzygy:
    """Return the most recent new/full moon before `when`.

    Uses the port's `last_lunation_before` to locate the event (which is
    ayanamsa-invariant — it only depends on Sun-Moon geometry). Then determines
    NEW vs FULL by comparing Sun and Moon longitudes at that moment, and
    re-queries the Moon's longitude in the requested zodiac so the returned
    longitude matches the rest of the chart.
    """
    if when.tzinfo is None:
        raise ValueError("compute_prenatal_syzygy requires a timezone-aware datetime")

    jd = julian_day(when)
    event_jd, tropical_moon_lon = ephemeris.last_lunation_before(jd)
    tropical_sun_lon = float(ephemeris.body_position(Planet.SUN, event_jd).longitude)
    elongation = abs(((tropical_moon_lon - tropical_sun_lon) + 180.0) % 360.0 - 180.0)
    kind = SyzygyKind.NEW_MOON if elongation < 90.0 else SyzygyKind.FULL_MOON

    # Re-query moon longitude in the chart's zodiac for presentation consistency.
    moon_lon_for_chart = float(
        ephemeris.body_position(Planet.MOON, event_jd, ayanamsa=ayanamsa).longitude
    )

    return Syzygy(
        kind=kind,
        when=_jd_to_utc(event_jd),
        longitude=Longitude(normalize_longitude(moon_lon_for_chart)),
    )


def _jd_to_utc(jd_ut: float) -> datetime:
    """Inverse of `julian_day` — convert a JD (UT) back to a UTC datetime."""
    # JD 2440587.5 == 1970-01-01T00:00:00Z (Unix epoch).
    seconds = (jd_ut - 2440587.5) * 86400.0
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)
