"""House system enum — which calculation method to use."""

from __future__ import annotations

from enum import Enum


class HouseSystem(Enum):
    """Traditional house systems, with single-char codes matching Swiss Ephemeris."""

    WHOLE_SIGN = "W"
    PORPHYRY = "O"
    ALCABITUS = "B"
    REGIOMONTANUS = "R"
    PLACIDUS = "P"
