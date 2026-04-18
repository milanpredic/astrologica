"""Public facade for the Chart aggregate and natal-chart computation.

The domain orchestrator (``_internal.domain.chart.compute.compute_natal_chart``)
requires an explicit ``EphemerisPort``. This facade wraps it and injects a default
``SwissEphemerisAdapter`` when the caller omits one — keeping the domain layer
independent of pyswisseph (enforced by the import-linter contract).
"""

from __future__ import annotations

from astrologica._internal.domain.chart import Chart
from astrologica._internal.domain.chart.chart_data import ChartData
from astrologica._internal.domain.chart.compute import compute_natal_chart as _compute_natal_chart
from astrologica._internal.domain.chart.tradition import ChartTradition
from astrologica._internal.domain.house.system import HouseSystem
from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter
from astrologica._internal.ports.ephemeris import EphemerisPort

__all__ = ["Chart", "ChartTradition", "compute_natal_chart"]


def compute_natal_chart(
    data: ChartData,
    house_system: HouseSystem = HouseSystem.WHOLE_SIGN,
    ephemeris: EphemerisPort | None = None,
    tradition: ChartTradition = ChartTradition.TRADITIONAL,
) -> Chart:
    """Compute a natal chart for `data`.

    `tradition` selects the body set:
    - `ChartTradition.TRADITIONAL` (default): the 7 classical planets.
    - `ChartTradition.MODERN`: classical + Uranus, Neptune, Pluto + lunar nodes.

    If `ephemeris` is None, a default `SwissEphemerisAdapter` is used — the most
    common path for library consumers. Inject a custom `EphemerisPort` for tests
    or alternate backends.
    """
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_natal_chart(data, house_system, adapter, tradition=tradition)
