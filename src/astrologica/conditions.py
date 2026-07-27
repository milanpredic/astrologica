"""Public facade for traditional chart conditions.

Via combusta, moon phase (quarters), besiegement (bodily + by rays), and the
void-of-course Moon (perfection-before-sign-exit criterion).
"""

from __future__ import annotations

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.conditions import (
    VIA_COMBUSTA_END,
    VIA_COMBUSTA_START,
    Besiegement,
    MoonPhase,
    MoonQuarter,
    NextPerfection,
    VoidOfCourse,
    compute_besiegement,
    compute_void_of_course,
    in_via_combusta,
    moon_phase,
)
from astrologica._internal.domain.planet.planet import Planet

__all__ = [
    "VIA_COMBUSTA_START",
    "VIA_COMBUSTA_END",
    "in_via_combusta",
    "MoonQuarter",
    "MoonPhase",
    "moon_phase",
    "compute_moon_phase",
    "Besiegement",
    "compute_besiegement",
    "chart_besiegement",
    "NextPerfection",
    "VoidOfCourse",
    "compute_void_of_course",
    "chart_void_of_course",
]


def compute_moon_phase(chart: Chart) -> MoonPhase:
    """Moon phase (quarter + waxing) of `chart`."""
    return moon_phase(
        float(chart.planets[Planet.SUN].position.longitude),
        float(chart.planets[Planet.MOON].position.longitude),
    )


def chart_besiegement(chart: Chart, planet: Planet) -> Besiegement:
    """Besiegement status of `planet` in `chart`."""
    return compute_besiegement(chart.planets, planet)


def chart_void_of_course(chart: Chart) -> VoidOfCourse:
    """Void-of-course status of the Moon in `chart`."""
    return compute_void_of_course(chart.planets)
