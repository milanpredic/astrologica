"""Traditional chart conditions — via combusta, moon phase, besiegement, VOC.

Pure functions over planet positions; no ephemeris access. The void-of-course
computation uses the classical *static* simplification (target planets held at
their natal longitudes while the Moon advances) — the method of the horary
sources themselves; the Moon outruns every other body, so the approximation
errs only by the slower planet's own motion across the remaining arc.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition

__all__ = [
    "VIA_COMBUSTA_START",
    "VIA_COMBUSTA_END",
    "in_via_combusta",
    "MoonQuarter",
    "MoonPhase",
    "moon_phase",
    "Besiegement",
    "compute_besiegement",
    "NextPerfection",
    "VoidOfCourse",
    "compute_void_of_course",
]

_MALEFICS = frozenset({Planet.MARS, Planet.SATURN})
_BENEFICS = frozenset({Planet.JUPITER, Planet.VENUS})
_PTOLEMAIC_ANGLES: tuple[float, ...] = (0.0, 60.0, 90.0, 120.0, 180.0)


# ---------------------------------------------------------------------------
# Via combusta
# ---------------------------------------------------------------------------

# The "burnt path": 15° Libra → 15° Scorpio (the standard span).
VIA_COMBUSTA_START = 195.0
VIA_COMBUSTA_END = 225.0


def in_via_combusta(longitude: float) -> bool:
    """True when `longitude` falls on the via combusta (15° Libra – 15° Scorpio)."""
    return VIA_COMBUSTA_START <= (longitude % 360.0) <= VIA_COMBUSTA_END


# ---------------------------------------------------------------------------
# Moon phase
# ---------------------------------------------------------------------------


class MoonQuarter(Enum):
    """Quarter by elongation from the Sun (0–90 / 90–180 / 180–270 / 270–360)."""

    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


@dataclass(frozen=True)
class MoonPhase:
    elongation: float  # Moon − Sun, 0..360
    quarter: MoonQuarter
    waxing: bool


def moon_phase(sun_longitude: float, moon_longitude: float) -> MoonPhase:
    elongation = (moon_longitude - sun_longitude) % 360.0
    quarter = MoonQuarter(int(elongation // 90.0) + 1)
    return MoonPhase(elongation=elongation, quarter=quarter, waxing=elongation < 180.0)


# ---------------------------------------------------------------------------
# Besiegement (obsessio)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Besiegement:
    """Malefic enclosure of one planet.

    `bodily` — the nearest planetary bodies on both zodiacal sides are Mars
    and Saturn (Lilly CA I p.113, *"betwixt the bodies of the two Malevolent
    Planets"*); arcs to the enclosing bodies are reported for the caller's
    orb policy. `by_rays` — the planet separates from one malefic and
    applies to the other by any Ptolemaic aspect (aspectual enclosure).
    `benefic_intervention` — an applying Ptolemaic aspect to a benefic
    perfects closer than the applying malefic contact, breaking the siege.
    """

    planet: Planet
    bodily: bool
    arc_to_prior: float | None  # arc back to the enclosing body behind
    arc_to_next: float | None  # arc forward to the enclosing body ahead
    by_rays: bool
    separating_from: Planet | None
    applying_to: Planet | None
    benefic_intervention: bool


def _forward_arc(from_lon: float, to_lon: float) -> float:
    return (to_lon - from_lon) % 360.0


def _aspect_offset(lon_a: float, lon_b: float) -> tuple[float, float]:
    """(separation, nearest Ptolemaic angle) between two longitudes."""
    sep = abs(lon_a - lon_b) % 360.0
    sep = min(sep, 360.0 - sep)
    nearest = min(_PTOLEMAIC_ANGLES, key=lambda angle: abs(sep - angle))
    return sep, nearest


def _is_applying_to(
    positions: Mapping[Planet, PlanetPosition], planet: Planet, other: Planet
) -> tuple[bool, float]:
    """(applying?, orb) of `planet`'s nearest Ptolemaic contact with `other`.

    Applying when the faster body moves toward exactness of the nearest
    Ptolemaic angle (direct-motion approximation on separations).
    """
    lon_p = float(positions[planet].position.longitude)
    lon_o = float(positions[other].position.longitude)
    sp_p = float(positions[planet].position.speed)
    sp_o = float(positions[other].position.speed)
    sep, nearest = _aspect_offset(lon_p, lon_o)
    orb = sep - nearest
    # Signed separation of other ahead of planet, in (-180, 180].
    signed = (lon_o - lon_p + 180.0) % 360.0 - 180.0
    relative_speed = sp_p - sp_o
    # The gap |signed| moves toward `nearest` when the faster body closes it.
    closing = (signed > 0 and relative_speed > 0) or (signed < 0 and relative_speed < 0)
    applying = closing if abs(signed) > nearest else not closing
    return applying, abs(orb)


def compute_besiegement(
    positions: Mapping[Planet, PlanetPosition],
    planet: Planet,
) -> Besiegement:
    """Besiegement status of `planet` (never a malefic itself)."""
    if planet in _MALEFICS:
        return Besiegement(planet, False, None, None, False, None, None, False)

    lon = float(positions[planet].position.longitude)
    others = [p for p in positions if p.is_classical and p is not planet]

    # Bodily: nearest body behind and ahead along the zodiac.
    behind = min(others, key=lambda p: _forward_arc(float(positions[p].position.longitude), lon))
    ahead = min(others, key=lambda p: _forward_arc(lon, float(positions[p].position.longitude)))
    bodily = {behind, ahead} == _MALEFICS
    arc_prior = _forward_arc(float(positions[behind].position.longitude), lon) if bodily else None
    arc_next = _forward_arc(lon, float(positions[ahead].position.longitude)) if bodily else None

    # By rays: separating from one malefic while applying to the other.
    mars_applying, mars_orb = _is_applying_to(positions, planet, Planet.MARS)
    saturn_applying, saturn_orb = _is_applying_to(positions, planet, Planet.SATURN)
    by_rays = mars_applying != saturn_applying
    separating_from: Planet | None = None
    applying_to: Planet | None = None
    applying_malefic_orb = 0.0
    if by_rays:
        if mars_applying:
            separating_from, applying_to = Planet.SATURN, Planet.MARS
            applying_malefic_orb = mars_orb
        else:
            separating_from, applying_to = Planet.MARS, Planet.SATURN
            applying_malefic_orb = saturn_orb

    benefic_intervention = False
    if by_rays:
        for benefic in _BENEFICS:
            if benefic not in positions:
                continue
            b_applying, b_orb = _is_applying_to(positions, planet, benefic)
            if b_applying and b_orb < applying_malefic_orb:
                benefic_intervention = True
                break

    return Besiegement(
        planet=planet,
        bodily=bodily,
        arc_to_prior=arc_prior,
        arc_to_next=arc_next,
        by_rays=by_rays,
        separating_from=separating_from,
        applying_to=applying_to,
        benefic_intervention=benefic_intervention,
    )


# ---------------------------------------------------------------------------
# Void of course (by perfection before sign exit)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NextPerfection:
    planet: Planet
    angle: float  # Ptolemaic aspect angle that perfects
    arc: float  # degrees the Moon travels until exactness


@dataclass(frozen=True)
class VoidOfCourse:
    """Moon void of course when no Ptolemaic aspect perfects before it
    leaves its sign (the perfection criterion — a late-degree Moon that
    still completes an aspect in-sign is *not* void)."""

    void: bool
    next_perfection: NextPerfection | None
    arc_to_sign_exit: float


def compute_void_of_course(
    positions: Mapping[Planet, PlanetPosition],
) -> VoidOfCourse:
    moon_lon = float(positions[Planet.MOON].position.longitude)
    sign_exit = (int(moon_lon // 30.0) + 1) * 30.0
    arc_to_exit = sign_exit - moon_lon

    best: NextPerfection | None = None
    for planet, pp in positions.items():
        if planet is Planet.MOON or not planet.is_classical:
            continue
        lon = float(pp.position.longitude)
        for angle in _PTOLEMAIC_ANGLES:
            for target in ((lon + angle) % 360.0, (lon - angle) % 360.0):
                arc = (target - moon_lon) % 360.0
                if 0.0 < arc <= arc_to_exit and (best is None or arc < best.arc):
                    best = NextPerfection(planet=planet, angle=angle, arc=arc)

    return VoidOfCourse(void=best is None, next_perfection=best, arc_to_sign_exit=arc_to_exit)
