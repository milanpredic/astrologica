"""Public facade for find_time — solve when a body reaches a longitude."""

from __future__ import annotations

from datetime import datetime

from astrologica._internal.domain.ayanamsa import Ayanamsa
from astrologica._internal.domain.find_time import find_time as _find_time
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.reference_frame import ReferenceFrame
from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter
from astrologica._internal.ports.ephemeris import EphemerisPort

__all__ = ["find_time"]


def find_time(
    body: Planet,
    target_longitude: float,
    start: datetime,
    end: datetime,
    ephemeris: EphemerisPort | None = None,
    ayanamsa: Ayanamsa | None = None,
    frame: ReferenceFrame = ReferenceFrame.GEOCENTRIC,
    place: Place | None = None,
) -> datetime | None:
    """First moment in `[start, end]` when `body` crosses `target_longitude`."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _find_time(
        body, target_longitude, start, end, adapter, ayanamsa=ayanamsa, frame=frame, place=place
    )
