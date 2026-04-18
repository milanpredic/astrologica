"""Angle primitives — Longitude, Latitude, Degree, Orb + helpers."""

from __future__ import annotations

from dataclasses import dataclass


def normalize_longitude(value: float) -> float:
    """Normalise any float to [0, 360)."""
    return value % 360.0


def shortest_arc(a: float, b: float) -> float:
    """Signed shortest arc from a → b in degrees, in (-180, 180]."""
    diff = (b - a + 180.0) % 360.0 - 180.0
    return 180.0 if diff == -180.0 else diff


@dataclass(frozen=True, slots=True, order=True)
class Longitude:
    """Ecliptic longitude in [0, 360). Self-normalising."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", normalize_longitude(self.value))

    def __float__(self) -> float:
        return self.value

    def arc_to(self, other: Longitude) -> float:
        """Signed shortest arc to `other`, in (-180, 180]."""
        return shortest_arc(self.value, other.value)


@dataclass(frozen=True, slots=True, order=True)
class Latitude:
    """Ecliptic (or geographic) latitude in [-90, 90]."""

    value: float

    def __post_init__(self) -> None:
        if not -90.0 <= self.value <= 90.0:
            raise ValueError(f"Latitude out of range: {self.value}")

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class Degree:
    """Bare degree wrapper for offsets inside a sign, orbs, etc."""

    value: float

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class Orb:
    """Orb in decimal degrees; always non-negative."""

    value: float

    def __post_init__(self) -> None:
        if self.value < 0.0:
            raise ValueError(f"Orb cannot be negative: {self.value}")

    def __float__(self) -> float:
        return self.value
