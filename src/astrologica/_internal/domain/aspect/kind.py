"""AspectKind enum — Ptolemaic + semisextile + quincunx."""

from __future__ import annotations

from enum import Enum


class AspectKind(Enum):
    """Supported aspects, keyed by their exact angular separation.

    Traditional / Hellenistic practice uses only the five Ptolemaic aspects
    (conjunction, sextile, square, trine, opposition). Horary and some medieval
    traditions add the semisextile (30°) and quincunx / inconjunct (150°) —
    weak, partile-sensitive aspects frequently consulted in question charts.
    """

    CONJUNCTION = 0
    SEMISEXTILE = 30
    SEXTILE = 60
    SQUARE = 90
    TRINE = 120
    QUINCUNX = 150
    OPPOSITION = 180

    @property
    def angle(self) -> float:
        return float(self.value)
