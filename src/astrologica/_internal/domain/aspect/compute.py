"""compute_aspects — the Ptolemaic aspects among a set of planet positions."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from itertools import combinations

from astrologica._internal.domain.aspect.aspect import Aspect
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


def compute_aspects(
    positions: Mapping[Planet, PlanetPosition],
    orb_policy: Callable[[AspectKind, Planet, Planet], float] | None = None,
) -> tuple[Aspect, ...]:
    """Return every aspect within orb between any two planets.

    `orb_policy(kind, planet_a, planet_b)` returns the allowed orb in degrees for
    the pair. Defaults to `default_orb` from `tables/aspect_angles.py`.

    Aspect ordering in the returned tuple: by (first.name, second.name, kind.value)
    for determinism. `first` is the slower body of the pair (smaller abs(speed)) —
    matching the traditional convention that the faster body "applies to" the slower.
    """
    policy = orb_policy or default_orb
    items = sorted(positions.items(), key=lambda kv: kv[0].name)
    results: list[Aspect] = []

    for (p1, pp1), (p2, pp2) in combinations(items, 2):
        lon1 = pp1.longitude
        lon2 = pp2.longitude
        raw = _signed_angular_separation(lon1, lon2)
        abs_sep = abs(raw)

        for kind in _ASPECT_KINDS:
            orb = abs_sep - kind.angle if kind.angle != 0.0 else abs_sep
            # For CONJUNCTION, abs_sep is already the orb (0°).
            allowed = policy(kind, p1, p2)
            if abs(orb) <= allowed:
                # Order the pair by decreasing speed of the second (faster) body.
                # `first` is the slower one.
                speed1 = abs(float(pp1.position.speed))
                speed2 = abs(float(pp2.position.speed))
                if speed1 < speed2:
                    first_planet, second_planet = p1, p2
                    first_pos, second_pos = pp1, pp2
                else:
                    first_planet, second_planet = p2, p1
                    first_pos, second_pos = pp2, pp1

                applying = _is_applying(
                    first_pos.longitude,
                    second_pos.longitude,
                    float(first_pos.position.speed),
                    float(second_pos.position.speed),
                    kind.angle,
                )
                results.append(
                    Aspect(
                        first=first_planet,
                        second=second_planet,
                        kind=kind,
                        orb=abs(orb),
                        applying=applying,
                        exact=abs(orb) <= _EXACTNESS_TOLERANCE,
                    )
                )
                break  # at most one aspect kind per pair

    results.sort(key=lambda a: (a.first.name, a.second.name, a.kind.value))
    return tuple(results)


def _is_applying(
    lon_slow: float, lon_fast: float, speed_slow: float, speed_fast: float, angle: float
) -> bool:
    """Is the faster body moving toward exactness of this aspect?

    We track the relative longitude `delta = lon_fast - lon_slow` (signed shortest arc)
    and ask whether its absolute value is decreasing toward `angle`. The relative
    angular velocity is `speed_fast - speed_slow`.
    """
    delta = _signed_angular_separation(lon_slow, lon_fast)
    abs_delta = abs(delta)
    rel_speed = speed_fast - speed_slow
    if angle == 0.0:
        # Conjunction: approaching when |delta| is shrinking.
        return (delta > 0 and rel_speed < 0) or (delta < 0 and rel_speed > 0)
    # For all other aspects exactness happens at abs_delta == angle.
    approaching = (abs_delta < angle and rel_speed * (1 if delta >= 0 else -1) > 0) or (
        abs_delta > angle and rel_speed * (1 if delta >= 0 else -1) < 0
    )
    return approaching
