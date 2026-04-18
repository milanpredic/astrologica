"""compute_fixed_star_conjunctions — conjunctions between chart bodies and fixed stars.

For each of the 30 classical fixed stars (`FixedStar` enum), check its
ecliptic longitude at the chart's moment against every body in the chart.
When the angular separation is within the orb (default 1°), report a
`FixedStarConjunction`.

The chart's ayanamsa is respected — sidereal chart → sidereal star longitudes.
"""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.fixed_stars_enum import FixedStar
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.tables.fixed_stars import SWE_STAR_NAMES
from astrologica._internal.ports.ephemeris import EphemerisPort


@dataclass(frozen=True, slots=True)
class FixedStarConjunction:
    """A body of the chart is within orb of a classical fixed star."""

    body: Planet
    star: FixedStar
    orb: float


def compute_fixed_star_conjunctions(
    chart: Chart,
    ephemeris: EphemerisPort,
    orb: float = 1.0,
) -> tuple[FixedStarConjunction, ...]:
    """Every (body, star) pairing within `orb` degrees at the chart's moment.

    Ordered by (body.name, star.name) for deterministic output.
    """
    jd = chart.data.jd
    ayanamsa = chart.data.ayanamsa

    star_lons: dict[FixedStar, float] = {}
    for star, swe_name in SWE_STAR_NAMES.items():
        try:
            star_lons[star] = ephemeris.fixed_star_longitude(swe_name, jd, ayanamsa=ayanamsa)
        except Exception:  # noqa: BLE001
            # A star not present in the ephemeris catalog is silently skipped —
            # keeps the function robust against missing fixstars.txt entries.
            continue

    results: list[FixedStarConjunction] = []
    for body, pp in chart.planets.items():
        body_lon = float(pp.longitude)
        for star, s_lon in star_lons.items():
            diff = abs((s_lon - body_lon + 180.0) % 360.0 - 180.0)
            if diff <= orb:
                results.append(FixedStarConjunction(body=body, star=star, orb=diff))

    results.sort(key=lambda c: (c.body.name, c.star.name))
    return tuple(results)
