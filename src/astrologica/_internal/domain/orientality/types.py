"""Orientality types — enum, no chart dependency."""

from __future__ import annotations

from enum import Enum


class Orientality(Enum):
    """Geometric state of a planet relative to the Sun."""

    ORIENTAL = "oriental"
    OCCIDENTAL = "occidental"
    NEUTRAL = "neutral"
