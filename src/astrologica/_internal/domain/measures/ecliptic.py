"""Ecliptic-frame position: raw output shape of an ephemeris query."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.measures.angle import Latitude, Longitude


@dataclass(frozen=True, slots=True)
class Speed:
    """Speed in ecliptic longitude, degrees per day. Negative = retrograde."""

    value: float

    @property
    def is_retrograde(self) -> bool:
        return self.value < 0.0

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True, slots=True)
class EclipticPosition:
    """A body's position in the ecliptic frame: longitude, latitude, daily speed."""

    longitude: Longitude
    latitude: Latitude
    speed: Speed
