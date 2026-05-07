"""compute_almuten — generic almuten computation over labeled chart points.

Essential scoring uses dignity_score with the caller's EssentialWeights.
Accidental scoring uses house-quality weights for each classical planet's
natal position. Modifiers (combust, retrograde, etc.) come from AlmutenModifiers.

Tie-break order, applied to top-scoring planets:
  1. Better house (ANGULAR > SUCCEDENT > CADENT)
  2. Sect-correct orientality (superior+oriental, inferior+occidental wins)
  3. Faster motion (higher absolute speed)
  4. Tightest aspect (smallest Ptolemaic-aspect orb) to nearest hyleg point

If all four passes still tie, winner=None and runners_up lists the tied
planets in input order.

Adapted from old_projects/morinus-console/almutens.py (structure: Essentials
+ Accidentals + Topicals split). Editorial weight numbers come from the
caller, not from Morinus' built-in scheme.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from astrologica._internal.domain.almuten.types import (
    DEFAULT_ACCIDENTAL_WEIGHTS,
    DEFAULT_ALMUTEN_MODIFIERS,
    AlmutenModifiers,
    AlmutenPoint,
    AlmutenPointBreakdown,
    AlmutenResult,
)
from astrologica._internal.domain.dignity.score import (
    LILLY_WEIGHTS,
    EssentialWeights,
    dignity_score,
)
from astrologica._internal.domain.house.placement import house_of
from astrologica._internal.domain.house.quality import HouseQuality, house_quality
from astrologica._internal.domain.orientality.compute import Orientality, planet_orientality
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition
from astrologica._internal.domain.sign import Sign
from astrologica._internal.domain.solar_state.compute import SolarState, planet_solar_state
from astrologica._internal.domain.tables.terms import TermsSystem

_CLASSICAL: tuple[Planet, ...] = (
    Planet.SUN,
    Planet.MOON,
    Planet.MERCURY,
    Planet.VENUS,
    Planet.MARS,
    Planet.JUPITER,
    Planet.SATURN,
)
_SUPERIORS: frozenset[Planet] = frozenset({Planet.MARS, Planet.JUPITER, Planet.SATURN})
_INFERIORS: frozenset[Planet] = frozenset({Planet.MERCURY, Planet.VENUS})
_MALEFICS: frozenset[Planet] = frozenset({Planet.MARS, Planet.SATURN})


def compute_almuten(
    chart: object,
    points: Sequence[AlmutenPoint],
    *,
    essential_weights: EssentialWeights = LILLY_WEIGHTS,
    accidental_weights: Mapping[HouseQuality, int] = DEFAULT_ACCIDENTAL_WEIGHTS,
    modifiers: AlmutenModifiers = DEFAULT_ALMUTEN_MODIFIERS,
    sect_aware: bool = True,
    terms_system: TermsSystem = TermsSystem.EGYPTIAN,
) -> AlmutenResult:
    """Generic almuten computation. See module docstring for tie-break rules."""
    is_diurnal = bool(getattr(chart, "is_diurnal"))
    planets: Mapping[Planet, PlanetPosition] = getattr(chart, "planets")
    houses = getattr(chart, "houses")
    asc_lon = float(getattr(chart, "ascendant"))

    # 1. Essentials per (point, planet).
    breakdown_list: list[AlmutenPointBreakdown] = []
    essential_totals: dict[Planet, int] = {p: 0 for p in _CLASSICAL}
    for point in points:
        per_planet: dict[Planet, int] = {}
        per_text: dict[Planet, str] = {}
        for planet in _CLASSICAL:
            score = dignity_score(
                planet,
                point.longitude,
                is_diurnal=is_diurnal if sect_aware else True,
                weights=essential_weights,
                terms_system=terms_system,
            )
            per_planet[planet] = score
            per_text[planet] = (("+" if score > 0 else "") + str(score)) if score != 0 else ""
            essential_totals[planet] += score
        breakdown_list.append(
            AlmutenPointBreakdown(
                point=point,
                sign=Sign.of(point.longitude),
                per_planet=per_planet,
                per_planet_text=per_text,
            )
        )

    # 2. Accidentals per planet (one-time, from natal placement).
    accidental_totals: dict[Planet, int] = {p: 0 for p in _CLASSICAL}
    for planet in _CLASSICAL:
        if planet not in planets:
            continue
        h = house_of(float(planets[planet].position.longitude), houses)
        if h is not None:
            quality = house_quality(h)
            accidental_totals[planet] += accidental_weights[quality]

    # 3. Modifiers per planet.
    modifier_totals: dict[Planet, int] = {p: 0 for p in _CLASSICAL}
    sun_pos = planets[Planet.SUN]
    for planet in _CLASSICAL:
        if planet not in planets:
            continue
        pp = planets[planet]
        m = 0

        state = planet_solar_state(pp, sun_pos)
        if state is SolarState.COMBUST:
            m += modifiers.combust
        elif state is SolarState.UNDER_BEAMS:
            m += modifiers.under_beams
        elif state is SolarState.CAZIMI:
            m += modifiers.cazimi

        if pp.is_retrograde:
            m += modifiers.retrograde

        diff = abs(((float(pp.position.longitude) - asc_lon) + 180.0) % 360.0 - 180.0)
        if not _has_ptolemaic_to_angle(diff):
            m += modifiers.aversion_to_asc

        ori = planet_orientality(planet, planets)
        if planet in _SUPERIORS and ori is Orientality.ORIENTAL:
            m += modifiers.oriental_bonus_superior
        if planet in _INFERIORS and ori is Orientality.OCCIDENTAL:
            m += modifiers.occidental_bonus_inferior

        if not pp.is_retrograde:
            m += modifiers.fast_or_direct_bonus

        h = house_of(float(pp.position.longitude), houses)
        if h is not None:
            q = house_quality(h)
            if q is HouseQuality.ANGULAR:
                m += modifiers.angular_house
            elif q is HouseQuality.SUCCEDENT:
                m += modifiers.succedent_house
            elif q is HouseQuality.CADENT:
                m += modifiers.cadent_house
            if planet in _MALEFICS and h in (6, 12):
                m += modifiers.malefic_in_6_or_12
        modifier_totals[planet] = m

    # 4. Total = essential + accidental + modifier.
    totals: dict[Planet, int] = {
        p: essential_totals[p] + accidental_totals[p] + modifier_totals[p] for p in _CLASSICAL
    }

    # 5. Resolve ties.
    winner, runners_up, trace = _resolve_winner(totals, planets, points, chart, sect_aware)

    return AlmutenResult(
        winner=winner,
        runners_up=tuple(runners_up),
        totals=totals,
        essential_totals=essential_totals,
        accidental_totals=accidental_totals,
        modifier_totals=modifier_totals,
        breakdown=tuple(breakdown_list),
        tie_break_trace=tuple(trace),
    )


def _has_ptolemaic_to_angle(diff: float) -> bool:
    """True if `diff` (0..180°) is within default orb of any Ptolemaic aspect angle."""
    targets = ((0.0, 8.0), (60.0, 4.0), (90.0, 6.0), (120.0, 7.0), (180.0, 8.0))
    return any(abs(diff - t) <= o for t, o in targets)


def _resolve_winner(
    totals: Mapping[Planet, int],
    planets: Mapping[Planet, PlanetPosition],
    points: Sequence[AlmutenPoint],
    chart: object,
    sect_aware: bool,
) -> tuple[Planet | None, list[Planet], list[str]]:
    trace: list[str] = []
    if not totals:
        return None, [], trace
    top_score = max(totals.values())
    candidates = [p for p, s in totals.items() if s == top_score]
    if len(candidates) == 1:
        return candidates[0], [], trace

    trace.append(f"tie at {top_score}: {[p.name for p in candidates]}")

    houses = getattr(chart, "houses")
    quality_rank = {HouseQuality.ANGULAR: 3, HouseQuality.SUCCEDENT: 2, HouseQuality.CADENT: 1}

    def _house_q_rank(p: Planet) -> int:
        if p not in planets:
            return 0
        h = house_of(float(planets[p].position.longitude), houses)
        if h is None:
            return 0
        return quality_rank[house_quality(h)]

    by_house = sorted(candidates, key=_house_q_rank, reverse=True)
    best_house = _house_q_rank(by_house[0])
    candidates = [p for p in by_house if _house_q_rank(p) == best_house]
    trace.append(f"after house-quality: {[p.name for p in candidates]}")
    if len(candidates) == 1:
        return candidates[0], [], trace

    def _orient_rank(p: Planet) -> int:
        ori = planet_orientality(p, planets)
        if p in _SUPERIORS and ori is Orientality.ORIENTAL:
            return 1
        if p in _INFERIORS and ori is Orientality.OCCIDENTAL:
            return 1
        return 0

    by_ori = sorted(candidates, key=_orient_rank, reverse=True)
    best_ori = _orient_rank(by_ori[0])
    candidates = [p for p in by_ori if _orient_rank(p) == best_ori]
    trace.append(f"after orientality: {[p.name for p in candidates]}")
    if len(candidates) == 1:
        return candidates[0], [], trace

    def _abs_speed(p: Planet) -> float:
        if p not in planets:
            return 0.0
        return abs(float(planets[p].position.speed))

    by_speed = sorted(candidates, key=_abs_speed, reverse=True)
    fastest = _abs_speed(by_speed[0])
    candidates = [p for p in by_speed if abs(_abs_speed(p) - fastest) < 1e-9]
    trace.append(f"after speed: {[p.name for p in candidates]}")
    if len(candidates) == 1:
        return candidates[0], [], trace

    def _tightest_orb(p: Planet) -> float:
        if p not in planets or not points:
            return 360.0
        pl_lon = float(planets[p].position.longitude)
        best = 360.0
        for pt in points:
            diff = abs(((pl_lon - pt.longitude) + 180.0) % 360.0 - 180.0)
            for target_angle in (0.0, 60.0, 90.0, 120.0, 180.0):
                best = min(best, abs(diff - target_angle))
        return best

    by_orb = sorted(candidates, key=_tightest_orb)
    tightest = _tightest_orb(by_orb[0])
    candidates = [p for p in by_orb if abs(_tightest_orb(p) - tightest) < 1e-9]
    trace.append(f"after tightest-aspect: {[p.name for p in candidates]}")
    if len(candidates) == 1:
        return candidates[0], [], trace

    return None, candidates, trace
