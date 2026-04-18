"""Place — Earth coordinate (latitude + longitude + optional altitude)."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.measures.angle import Latitude


@dataclass(frozen=True, slots=True)
class Place:
    """Earth coordinate. Longitude here is geographic (East positive), in [-180, 180].

    `altitude` is in metres above sea level; it only matters for topocentric
    positions (observer-relative, parallax-corrected), where the Moon can shift
    by up to ~1° at the horizon relative to the geocentric position.
    """

    latitude: float
    longitude: float
    altitude: float = 0.0

    def __post_init__(self) -> None:
        Latitude(self.latitude)  # validate range
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError(f"Geographic longitude out of range: {self.longitude}")
