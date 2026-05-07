"""compute_aspects — Ptolemaic aspects among planets, optionally including angles."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from itertools import combinations

from astrologica._internal.domain.aspect.angle import Angle
from astrologica._internal.domain.aspect.aspect import Aspect, AspectEndpoint
from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition
from astrologica._internal.domain.tables.aspect_angles import default_orb

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


def _signed_angular_separation(a: float, b: float) -> float:
    """Shortest arc from a to b, in (-180, 180]."""
    diff = (b - a + 180.0) % 360.0 - 180.0
    return 180.0 if diff == -180.0 else diff


def _angle_longitude(angle: Angle, ascendant: float, midheaven: float) -> float:
    if angle is Angle.ASCENDANT:
        return ascendant
    if angle is Angle.MIDHEAVEN:
        return midheaven
    if angle is Angle.DESCENDANT:
        return (ascendant + 180.0) % 360.0
    return (midheaven + 180.0) % 360.0  # IC


def _endpoint_name(e: AspectEndpoint) -> str:
    return e.name


def _default_orb_for_endpoints(kind: AspectKind, a: AspectEndpoint, b: AspectEndpoint) -> float:
    """Wrap default_orb so angle endpoints are accepted (treated as non-luminary)."""
    pa = a if isinstance(a, Planet) else Planet.SATURN
    pb = b if isinstance(b, Planet) else Planet.SATURN
    return default_orb(kind, pa, pb)


def compute_aspects(
    positions: Mapping[Planet, PlanetPosition],
    orb_policy: Callable[[AspectKind, AspectEndpoint, AspectEndpoint], float] | None = None,
    *,
    include_angles: Sequence[Angle] = (),
    chart: object | None = None,
) -> tuple[Aspect, ...]:
    """Return every aspect within orb between any two endpoints.

    `orb_policy(kind, endpoint_a, endpoint_b)` returns the allowed orb in degrees.
    Defaults to `default_orb` from `tables/aspect_angles.py`.

    `include_angles` selects which cardinal angles to include. When non-empty,
    `chart` must be supplied so the angle longitudes can be resolved.

    Aspect ordering: by (first.name, second.name, kind.value) for determinism.
    `first` is the slower body of the pair (smaller abs(speed)). For angle
    endpoints, the angle is treated as static (speed 0) and `applying`
    reflects the planet's motion only.
    """
    policy = orb_policy or _default_orb_for_endpoints

    endpoints: list[tuple[AspectEndpoint, float, float]] = []
    for planet, pp in sorted(positions.items(), key=lambda kv: kv[0].name):
        endpoints.append((planet, float(pp.position.longitude), float(pp.position.speed)))

    if include_angles:
        if chart is None:
            raise ValueError("compute_aspects(include_angles=...) requires chart=...")
        ascendant = float(getattr(chart, "ascendant"))
        midheaven = float(getattr(chart, "midheaven"))
        for angle in include_angles:
            lon = _angle_longitude(angle, ascendant, midheaven)
            endpoints.append((angle, lon, 0.0))

    results: list[Aspect] = []
    for (e1, lon1, sp1), (e2, lon2, sp2) in combinations(endpoints, 2):
        raw = _signed_angular_separation(lon1, lon2)
        abs_sep = abs(raw)

        for kind in _ASPECT_KINDS:
            orb = abs_sep - kind.angle if kind.angle != 0.0 else abs_sep
            allowed = policy(kind, e1, e2)
            if abs(orb) <= allowed:
                if abs(sp1) < abs(sp2):
                    first, second, first_lon, second_lon, first_sp, second_sp = (
                        e1,
                        e2,
                        lon1,
                        lon2,
                        sp1,
                        sp2,
                    )
                else:
                    first, second, first_lon, second_lon, first_sp, second_sp = (
                        e2,
                        e1,
                        lon2,
                        lon1,
                        sp2,
                        sp1,
                    )
                applying = _is_applying(first_lon, second_lon, first_sp, second_sp, kind.angle)
                results.append(
                    Aspect(
                        first=first,
                        second=second,
                        kind=kind,
                        orb=abs(orb),
                        applying=applying,
                        exact=abs(orb) <= _EXACTNESS_TOLERANCE,
                    )
                )
                break

    results.sort(key=lambda a: (_endpoint_name(a.first), _endpoint_name(a.second), a.kind.value))
    return tuple(results)


def _is_applying(
    lon_slow: float, lon_fast: float, speed_slow: float, speed_fast: float, angle: float
) -> bool:
    """Is the faster body moving toward exactness of this aspect?"""
    delta = _signed_angular_separation(lon_slow, lon_fast)
    abs_delta = abs(delta)
    rel_speed = speed_fast - speed_slow
    if angle == 0.0:
        return (delta > 0 and rel_speed < 0) or (delta < 0 and rel_speed > 0)
    approaching = (abs_delta < angle and rel_speed * (1 if delta >= 0 else -1) > 0) or (
        abs_delta > angle and rel_speed * (1 if delta >= 0 else -1) < 0
    )
    return approaching
