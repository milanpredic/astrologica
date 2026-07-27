"""Public facade for planetary sect conditions (in-sect / halb / hayz)."""

from __future__ import annotations

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sect import (
    PlanetSect,
    SectStatus,
    compute_sect_statuses,
)

__all__ = ["PlanetSect", "SectStatus", "compute_sect_statuses", "compute_sect_status"]


def compute_sect_status(chart: Chart) -> dict[Planet, SectStatus]:
    """Sect / halb / hayz status for every classical planet in `chart`."""
    return compute_sect_statuses(
        chart.planets,
        ascendant=float(chart.ascendant),
        is_diurnal=chart.is_diurnal,
    )
