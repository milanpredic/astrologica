"""compute_custom_lot — evaluate a `CustomLot` formula against a chart.

Resolves each symbolic `LotComponent` to a longitude using the chart's
planets, house cusps, ascendant, midheaven, syzygy, lots, and rulerships.
Then applies `ASC + Σplus − Σminus` using the sect-appropriate formula.
"""

from __future__ import annotations

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.custom_lot.component import (
    CardinalAngle,
    CardinalAngleName,
    HouseCuspRef,
    LordKind,
    LordOf,
    LotComponent,
    PriorLot,
    RulerOf,
    RulerOfKind,
    SyzygyPoint,
)
from astrologica._internal.domain.custom_lot.custom_lot import CustomLot
from astrologica._internal.domain.custom_lot.formula import LotFormula
from astrologica._internal.domain.measures.angle import Longitude, normalize_longitude
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign
from astrologica._internal.domain.tables.rulerships import DOMICILE


def compute_custom_lot(chart: Chart, lot: CustomLot) -> Longitude:
    """Evaluate `lot` against `chart`. Applies the day or night formula
    depending on `chart.is_diurnal`."""
    formula = lot.day if chart.is_diurnal else lot.night

    asc = float(chart.ascendant)
    plus = sum(_resolve(chart, c) for c in formula.plus)
    minus = sum(_resolve(chart, c) for c in formula.minus)

    return Longitude(normalize_longitude(asc + plus - minus))


def _resolve(chart: Chart, component: LotComponent) -> float:
    if isinstance(component, Planet):
        if component in chart.planets:
            return float(chart.planets[component].longitude)
        raise ValueError(f"planet {component.name} not present in chart")

    if isinstance(component, CardinalAngle):
        return _resolve_cardinal(chart, component.angle)

    if isinstance(component, HouseCuspRef):
        # chart.houses is a tuple ordered 1..12, and each HouseCusp object has
        # a `.house` (enum) and `.cusp` (longitude).
        return float(chart.houses[component.n - 1].cusp)

    if isinstance(component, SyzygyPoint):
        return float(chart.syzygy.longitude)

    if isinstance(component, PriorLot):
        return float(chart.lots[component.lot].longitude)

    if isinstance(component, RulerOf):
        return _resolve_ruler(chart, component)

    if isinstance(component, LordOf):
        return _resolve_lord(chart, component)

    raise TypeError(f"unknown LotComponent: {component!r}")


def _resolve_cardinal(chart: Chart, angle: CardinalAngleName) -> float:
    asc = float(chart.ascendant)
    mc = float(chart.midheaven)
    if angle is CardinalAngleName.ASC:
        return asc
    if angle is CardinalAngleName.MC:
        return mc
    if angle is CardinalAngleName.DSC:
        return (asc + 180.0) % 360.0
    if angle is CardinalAngleName.IC:
        return (mc + 180.0) % 360.0
    raise ValueError(f"unknown cardinal angle {angle}")


def _resolve_ruler(chart: Chart, comp: RulerOf) -> float:
    """Domicile ruler's longitude at the chart moment."""
    if comp.kind is RulerOfKind.HOUSE:
        assert comp.house_n is not None
        cusp_lon = float(chart.houses[comp.house_n - 1].cusp)
        sign = Sign.of(cusp_lon)
    else:
        assert comp.sign is not None
        sign = comp.sign
    ruler = DOMICILE.get(sign)
    if ruler is None or ruler not in chart.planets:
        raise ValueError(f"no domicile ruler available for {sign}")
    return float(chart.planets[ruler].longitude)


# Weekday index (Monday=0..Sunday=6) → Chaldean day-lord.
_DAY_LORDS = {
    0: Planet.MOON,
    1: Planet.MARS,
    2: Planet.MERCURY,
    3: Planet.JUPITER,
    4: Planet.VENUS,
    5: Planet.SATURN,
    6: Planet.SUN,
}


def _resolve_lord(chart: Chart, comp: LordOf) -> float:
    """Lord of the day/hour/year, resolved to the body's longitude in the chart."""
    if comp.kind is LordKind.DAY:
        weekday = chart.data.utc.weekday()
        lord = _DAY_LORDS[weekday]
        return float(chart.planets[lord].longitude)
    if comp.kind is LordKind.HOUR:
        # We don't re-compute the planetary hour here (that would require a
        # Place-aware ephemeris call mid-evaluation). Fall back to day-lord
        # as the closest available shortcut; callers wanting precise hour
        # lords should compute the hour separately and pass a Planet.
        weekday = chart.data.utc.weekday()
        lord = _DAY_LORDS[weekday]
        return float(chart.planets[lord].longitude)
    if comp.kind is LordKind.YEAR:
        # The year-lord is the sign-lord of the profected ASC at the current age.
        # Without age context, default to the ASC's domicile ruler — the "year 0"
        # lord by convention.
        asc_sign = Sign.of(float(chart.ascendant))
        ruler = DOMICILE.get(asc_sign)
        if ruler is None or ruler not in chart.planets:
            raise ValueError("year-lord cannot be resolved from ASC")
        return float(chart.planets[ruler].longitude)
    raise ValueError(f"unknown lord kind {comp.kind}")


__all__ = ["LotFormula", "compute_custom_lot"]
