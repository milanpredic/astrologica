"""ChartTradition — selects which bodies appear in a chart.

`TRADITIONAL` restricts to the 7 classical planets (what traditional/Hellenistic
astrology uses). `MODERN` adds the outer planets (Uranus/Neptune/Pluto) and
lunar nodes (True + Mean + their antipodes).

This is a body-set selector only; it doesn't change house systems, aspect sets,
or dignities. Outer planets and nodes simply hold no essential dignities under
traditional tables, which is correct.
"""

from __future__ import annotations

from enum import Enum

from astrologica._internal.domain.planet.planet import Planet


class ChartTradition(Enum):
    """Which celestial bodies are included in a chart."""

    TRADITIONAL = "traditional"
    MODERN = "modern"

    def bodies(self) -> frozenset[Planet]:
        """The body set corresponding to this tradition."""
        if self is ChartTradition.TRADITIONAL:
            return Planet.classical()
        return Planet.modern()
