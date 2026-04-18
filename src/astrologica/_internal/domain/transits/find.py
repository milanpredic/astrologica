"""find_transits — range search for exact transit events in a window.

Algorithm: for each (transiting, natal, aspect) triple, walk the window at a
step calibrated to the transiting body's mean speed, watching for zero
crossings of an aspect-specific residual function. Each detected crossing is
then bisected to ~1-minute precision.

Residual choice:
- For conjunction (angle 0°) and opposition (angle 180°), use `sin(sep_rad)`.
  This has zeros at both 0° and ±180°, so we disambiguate after finding a
  crossing by checking whether the separation is near 0° or near 180°.
- For all other aspects (angle A ∈ {30, 60, 90, 120, 150}), use `cos(sep) −
  cos(A)`. This has clean sign-change zeros at sep = ±A (both geometrically
  valid aspect configurations) and no spurious zeros elsewhere.

Both residuals are continuous away from the sep-wrap boundary (±180°); wrap
jumps are filtered by treating samples whose residual changes by more than a
large threshold as discontinuities to skip.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from datetime import UTC, datetime, timedelta

from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.measures.jd import julian_day
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.transits.event import TransitEvent
from astrologica._internal.ports.ephemeris import EphemerisPort

_DEFAULT_ASPECTS: tuple[AspectKind, ...] = (
    AspectKind.CONJUNCTION,
    AspectKind.SEXTILE,
    AspectKind.SQUARE,
    AspectKind.TRINE,
    AspectKind.OPPOSITION,
)

# Samples whose residual jumps by more than this are assumed to be a sep-wrap
# artefact (sep crossing ±180) rather than a genuine aspect crossing.
_WRAP_JUMP_THRESHOLD = 1.0


def _signed_separation(a: float, b: float) -> float:
    diff = (b - a + 180.0) % 360.0 - 180.0
    return 180.0 if diff == -180.0 else diff


def _jd_to_utc(jd_ut: float) -> datetime:
    seconds = (jd_ut - 2440587.5) * 86400.0
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)


def _step_days_for(body: Planet) -> float:
    """Sampling step for bracketing — tighter for faster bodies."""
    if body is Planet.MOON:
        return 0.25  # 6h
    if body in (Planet.SUN, Planet.MERCURY, Planet.VENUS, Planet.MARS):
        return 1.0
    return 2.0  # Jupiter, Saturn, outers, nodes


def find_transits(
    natal: Chart,
    start: datetime,
    end: datetime,
    ephemeris: EphemerisPort,
    transiting_bodies: Iterable[Planet] | None = None,
    natal_bodies: Iterable[Planet] | None = None,
    aspects: Iterable[AspectKind] | None = None,
) -> tuple[TransitEvent, ...]:
    """All exact transit crossings in `[start, end]`."""
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("find_transits requires timezone-aware start/end")
    if end <= start:
        return ()

    t_bodies = (
        natal.tradition.bodies() if transiting_bodies is None else frozenset(transiting_bodies)
    )
    n_bodies = frozenset(natal.planets.keys()) if natal_bodies is None else frozenset(natal_bodies)
    selected_aspects = tuple(_DEFAULT_ASPECTS if aspects is None else aspects)

    jd_start = julian_day(start.astimezone(UTC))
    jd_end = julian_day(end.astimezone(UTC))
    ayanamsa = natal.data.ayanamsa
    frame = natal.data.frame
    place = natal.data.place

    def transit_lon(body: Planet, jd: float) -> float:
        return float(
            ephemeris.body_position(body, jd, ayanamsa=ayanamsa, frame=frame, place=place).longitude
        )

    events: list[TransitEvent] = []

    for t_body in t_bodies:
        step = _step_days_for(t_body)
        for n_body in n_bodies:
            natal_lon = float(natal.planets[n_body].longitude)
            for kind in selected_aspects:
                angle = kind.angle
                residual = _residual_factory(kind, natal_lon, t_body, transit_lon)

                prev_jd = jd_start
                prev_val = residual(prev_jd)
                jd = prev_jd + step
                while jd <= jd_end + 1e-9:
                    val = residual(jd)
                    jump = abs(val - prev_val)
                    is_wrap = jump > _WRAP_JUMP_THRESHOLD
                    if not is_wrap and prev_val * val < 0.0:
                        event_jd = _bisect(residual, prev_jd, jd, prev_val, val)
                        # For conjunction/opposition, disambiguate by actual sep.
                        sep_at_event = _signed_separation(natal_lon, transit_lon(t_body, event_jd))
                        if _matches_aspect(kind, sep_at_event):
                            events.append(
                                TransitEvent(
                                    when=_jd_to_utc(event_jd),
                                    transiting=t_body,
                                    natal=n_body,
                                    kind=kind,
                                    applying_before=_applying_before(
                                        angle, sep_at_event, prev_val, val
                                    ),
                                )
                            )
                    prev_jd, prev_val = jd, val
                    jd += step

    events.sort(key=lambda e: (e.when, e.natal.name, e.transiting.name, e.kind.value))
    return tuple(events)


def _residual_factory(
    kind: AspectKind,
    natal_lon: float,
    t_body: Planet,
    transit_lon: Callable[[Planet, float], float],
) -> Callable[[float], float]:
    """Return the residual function whose zero-crossings mark this aspect's
    exactness."""
    angle = kind.angle
    if angle == 0.0 or angle == 180.0:
        # sin(sep) zeros at sep = 0 and sep = ±180 — both the aspect we want
        # (conj/opp) and its antipode. _matches_aspect filters.
        def r_sin(jd: float) -> float:
            sep = _signed_separation(natal_lon, transit_lon(t_body, jd))
            return math.sin(math.radians(sep))

        return r_sin

    cos_angle = math.cos(math.radians(angle))

    def r_cos(jd: float) -> float:
        sep = _signed_separation(natal_lon, transit_lon(t_body, jd))
        return math.cos(math.radians(sep)) - cos_angle

    return r_cos


def _matches_aspect(kind: AspectKind, sep: float) -> bool:
    """Does the observed separation correspond to this aspect?"""
    abs_sep = abs(sep)
    # 5° tolerance is comfortably wider than our bisection precision but narrow
    # enough to distinguish conjunction from opposition.
    return abs(abs_sep - kind.angle) < 5.0


def _applying_before(
    angle: float, sep_at_event: float, prev_residual: float, post_residual: float
) -> bool:
    """Was the aspect applying just before exactness?

    For non-singular aspects (the cos-residual path), residual > 0 means
    |sep| < angle (closer to conjunction) and < 0 means |sep| > angle. The body
    is applying if |sep| is approaching |angle|, i.e. residual is moving from
    negative to zero (|sep| shrinking toward angle) — applying_before = True
    when prev_residual < 0.

    For conjunction/opposition (sin-residual), we use the fact that sin crosses
    from one sign to the other through zero; before exactness, the body is on
    one approach side. This flag is less definitive for these aspects but
    still meaningful.
    """
    if angle == 0.0 or angle == 180.0:
        return prev_residual < 0.0
    return prev_residual < 0.0


def _bisect(
    f: Callable[[float], float],
    lo: float,
    hi: float,
    f_lo: float,
    f_hi: float,
    max_iter: int = 40,
    tol: float = 1.0 / 1440.0,  # 1 minute as JD fraction
) -> float:
    """Bisect to find the root of `f` within `[lo, hi]` to ~1 minute precision."""
    _ = f_hi  # unused, kept in signature for callers that already compute both endpoints
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        f_mid = f(mid)
        if (hi - lo) < tol:
            return mid
        if f_lo * f_mid <= 0.0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2.0
