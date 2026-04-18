"""Dignity enum — essential-dignity categories."""

from __future__ import annotations

from enum import Enum


class Dignity(Enum):
    """Essential dignities of a planet in a sign.

    `DOMICILE` is also called "rulership" in some sources — they refer to the same
    relationship (the planet that owns the sign).
    """

    DOMICILE = "domicile"
    EXALTATION = "exaltation"
    TRIPLICITY = "triplicity"
    TERM = "term"
    FACE = "face"
    DETRIMENT = "detriment"
    FALL = "fall"
