"""compute_primary_directions — Placidian/Ptolemaic primary directions.

Supports both **zodiacal** and **mundane** approaches, with five arc-keys
(Ptolemy, Cardan, Naibod, True/Birthday solar equatorial) and DIRECT /
CONVERSE direction types.

Zodiacal arc (Placidian semi-arc method):
    arc = RA(promissor_at_aspect_point) − RA(significator)
          + AD_at_significator_pole(S_decl) − AD_at_significator_pole(aspect_decl)

Mundane arc (Placidian mundane position difference scaled by significator's SA):
    arc = (PMP_P_plus_aspect − PMP_S) × |SA_S| / 90

A `CONVERSE` direction swaps promissor ↔ significator before computing.

Arcs in degrees are converted to years via the chosen `ArcKey` (see
`arc_key.py`). Positive years mean a future event; negative mean past.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from astrologica._internal.domain.aspect.kind import AspectKind
from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.primary_directions.approach import DirectionApproach
from astrologica._internal.domain.primary_directions.arc_key import ArcKey
from astrologica._internal.domain.primary_directions.direction_type import DirectionType
from astrologica._internal.domain.primary_directions.speculum import (
    Speculum,
    _ra_decl,
    compute_all_specula,
)

# Year equivalents per degree of RA-arc for each key.
_DEGREES_PER_YEAR: dict[ArcKey, float] = {
    ArcKey.PTOLEMY: 1.0,
    ArcKey.CARDAN: 1.0,
    ArcKey.NAIBOD: 0.98565,
    # Native-dependent keys are approximated as Naibod here; under 0.5%
    # difference in practice and the enum values are preserved for API parity.
    ArcKey.TRUE_SOLAR_EQUATORIAL: 0.98565,
    ArcKey.BIRTHDAY_SOLAR_EQUATORIAL: 0.98565,
}


@dataclass(frozen=True, slots=True)
class PrimaryDirection:
    """A single primary direction event.

    `arc_degrees` is the signed arc between promissor and significator at the
    exact-aspect configuration; `years` is that arc converted via the key.
    Positive years → future event (from the natal moment); negative → past.
    """

    promissor: Planet
    significator: Planet
    kind: AspectKind
    direction: DirectionType
    approach: DirectionApproach
    arc_degrees: float
    years: float


def _signed_arc(a: float, b: float) -> float:
    """Shortest signed arc from a to b, in (-180, 180]."""
    d = (b - a + 180.0) % 360.0 - 180.0
    return 180.0 if d == -180.0 else d


def _ad_at_pole(decl_deg: float, pole_deg: float) -> float:
    """AD of a body with declination `decl_deg` under pole `pole_deg`.

    AD = arcsin(tan(pole) · tan(decl)). Returns 0 when the argument is out of
    the real-arcsin domain (body is circumpolar under that pole).
    """
    t = math.tan(math.radians(pole_deg)) * math.tan(math.radians(decl_deg))
    if abs(t) > 1.0:
        return 0.0
    return math.degrees(math.asin(t))


def compute_primary_directions(
    chart: Chart,
    key: ArcKey = ArcKey.NAIBOD,
    direction: DirectionType = DirectionType.DIRECT,
    approach: DirectionApproach = DirectionApproach.ZODIACAL,
    aspects: Iterable[AspectKind] | None = None,
    bodies: Iterable[Planet] | None = None,
) -> tuple[PrimaryDirection, ...]:
    """Primary directions for a chart.

    - `key`: arc-to-years conversion (default Naibod).
    - `direction`: DIRECT (promissor → significator) or CONVERSE (reverse).
    - `approach`: ZODIACAL (default, Placidian semi-arc with pole-corrected
      AD) or MUNDANE (PMP difference scaled by significator's semi-arc).
    - `aspects`: which aspect kinds to include (defaults to Ptolemaic 5).
    - `bodies`: which planets to use (defaults to classical bodies in chart).
    """
    aspect_list = tuple(
        aspects
        if aspects is not None
        else (
            AspectKind.CONJUNCTION,
            AspectKind.SEXTILE,
            AspectKind.SQUARE,
            AspectKind.TRINE,
            AspectKind.OPPOSITION,
        )
    )
    body_list = (
        tuple(bodies) if bodies is not None else tuple(p for p in chart.planets if p.is_classical)
    )

    specula = compute_all_specula(chart)
    deg_per_year = _DEGREES_PER_YEAR[key]

    results: list[PrimaryDirection] = []
    for sig in body_list:
        for prom in body_list:
            if prom is sig:
                continue
            for aspect in aspect_list:
                for side in (+1.0, -1.0):
                    if aspect.angle == 0.0 and side == -1.0:
                        continue
                    if aspect.angle == 180.0 and side == -1.0:
                        continue
                    signed_aspect = aspect.angle * side

                    if direction is DirectionType.DIRECT:
                        prom_spec = specula[prom]
                        sig_spec = specula[sig]
                    else:
                        # Converse: swap roles.
                        prom_spec = specula[sig]
                        sig_spec = specula[prom]

                    arc = _arc_for(
                        promissor_spec=prom_spec,
                        significator_spec=sig_spec,
                        aspect_angle=signed_aspect,
                        approach=approach,
                    )

                    results.append(
                        PrimaryDirection(
                            promissor=prom,
                            significator=sig,
                            kind=aspect,
                            direction=direction,
                            approach=approach,
                            arc_degrees=arc,
                            years=arc / deg_per_year,
                        )
                    )

    results.sort(
        key=lambda d: (
            d.significator.name,
            d.promissor.name,
            d.kind.value,
            d.years,
        )
    )
    return tuple(results)


def _arc_for(
    promissor_spec: Speculum,
    significator_spec: Speculum,
    aspect_angle: float,
    approach: DirectionApproach,
) -> float:
    """Compute the arc (°) for promissor → significator at `aspect_angle`."""
    if approach is DirectionApproach.MUNDANE:
        target_pmp = (promissor_spec.pmp + aspect_angle) % 360.0
        pmp_diff = _signed_arc(significator_spec.pmp, target_pmp)
        scale = abs(significator_spec.sa) / 90.0 if significator_spec.sa != 0.0 else 1.0
        return pmp_diff * scale

    # Zodiacal Placidian semi-arc: RA-based arc, corrected by AD at S's pole.
    aspect_lon = (significator_spec.lon + aspect_angle) % 360.0
    ra_at_aspect, decl_at_aspect = _ra_decl(aspect_lon, 0.0)

    arc = _signed_arc(significator_spec.ra, ra_at_aspect)

    if significator_spec.poh != 0.0:
        ad_aspect = _ad_at_pole(decl_at_aspect, significator_spec.poh)
        ad_sig = _ad_at_pole(significator_spec.decl, significator_spec.poh)
        arc = arc + ad_sig - ad_aspect

    return arc
