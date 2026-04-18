"""SyzygyKind — whether the last lunation before birth was a new moon or full moon."""

from __future__ import annotations

from enum import Enum


class SyzygyKind(Enum):
    NEW_MOON = "new_moon"
    FULL_MOON = "full_moon"
