"""compute_transits — snapshot aspects between transiting positions and a natal chart."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime

from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.planet.compute import compute_planet_positions
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition
from astrologica._internal.domain.tables.aspect_angles import default_orb
from astrologica._internal.domain.transits.aspect import TransitAspect
from astrologica._internal.ports.ephemeris import EphemerisPort

_EXACTNESS_TOLERANCE = 1e-6
_ASPECT_KINDS: tuple[AspectKind, ...] = (
    AspectKind.CONJUNCTION,
    AspectKind.SEMISEXTILE,
    AspectKind.SEXTILE,
    AspectKind.SQUARE,
    AspectKind.TRINE,
    AspectKind.QUINCUNX,
    AspectKind.OPPOSITION,
)


def _signed_separation(a: float, b: float) -> float:
    diff = (b - a + 180.0) % 360.0 - 180.0
    return 180.0 if diff == -180.0 else diff


def compute_transits(
    natal: Chart,
    when: datetime,
    ephemeris: EphemerisPort,
    orb_policy: Callable[[AspectKind, Planet, Planet], float] | None = None,
) -> tuple[TransitAspect, ...]:
    """Aspects between transiting bodies at `when` and placements in `natal`.

    Transiting bodies use the natal chart's `tradition` and inherit the natal's
    ayanamsa / frame so the two position sets live in the same zodiac.
    `orb_policy(kind, transiting, natal)` returns the allowed orb; defaults to
    the library's `default_orb`.

    Ordering: by (natal.name, transiting.name, kind.value).
    """
    policy = orb_policy or default_orb
    bodies = natal.tradition.bodies()
    transiting = compute_planet_positions(
        when,
        ephemeris,
        bodies=bodies,
        ayanamsa=natal.data.ayanamsa,
        frame=natal.data.frame,
        place=natal.data.place,
    )
    natal_positions: Mapping[Planet, PlanetPosition] = natal.planets

    results: list[TransitAspect] = []
    for t_planet, t_pos in transiting.items():
        for n_planet, n_pos in natal_positions.items():
            raw = _signed_separation(n_pos.longitude, t_pos.longitude)
            abs_sep = abs(raw)
            for kind in _ASPECT_KINDS:
                orb = abs_sep - kind.angle if kind.angle != 0.0 else abs_sep
                if abs(orb) > policy(kind, t_planet, n_planet):
                    continue
                applying = _is_applying(
                    n_pos.longitude,
                    t_pos.longitude,
                    float(t_pos.position.speed),
                    kind.angle,
                )
                results.append(
                    TransitAspect(
                        transiting=t_planet,
                        natal=n_planet,
                        kind=kind,
                        orb=abs(orb),
                        applying=applying,
                        exact=abs(orb) <= _EXACTNESS_TOLERANCE,
                    )
                )
                break  # at most one aspect kind per transit→natal pairing

    results.sort(key=lambda a: (a.natal.name, a.transiting.name, a.kind.value))
    return tuple(results)


def _is_applying(
    natal_lon: float,
    transit_lon: float,
    transit_speed: float,
    aspect_angle: float,
) -> bool:
    """Is the transiting body moving toward exactness of this aspect?

    Natal is fixed. `delta = transit_lon - natal_lon` in (-180, 180]. The
    aspect is applying when |delta| is changing toward aspect_angle.
    """
    delta = _signed_separation(natal_lon, transit_lon)
    abs_delta = abs(delta)
    if aspect_angle == 0.0:
        return (delta > 0 and transit_speed < 0) or (delta < 0 and transit_speed > 0)
    sign_of_delta = 1.0 if delta >= 0 else -1.0
    return (abs_delta < aspect_angle and transit_speed * sign_of_delta > 0) or (
        abs_delta > aspect_angle and transit_speed * sign_of_delta < 0
    )
