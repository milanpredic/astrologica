"""ChartData — input bundle for chart calculations.

Fields:
- `datetime`: timezone-aware birth moment.
- `place`: geographic location.
- `ayanamsa`: if set, all positions (planets + house cusps) are sidereal rather
  than tropical, using the named Swiss Ephemeris ayanamsa.

Derived accessors `.utc` and `.jd` feed calculations; `.datetime` preserves the
original tz for presentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime as _datetime

from astrologica._internal.domain.ayanamsa import Ayanamsa
from astrologica._internal.domain.measures.jd import julian_day
from astrologica._internal.domain.place import Place
from astrologica._internal.domain.reference_frame import ReferenceFrame


@dataclass(frozen=True, slots=True)
class ChartData:
    """Canonical who/when/where input for any chart calculation."""

    datetime: _datetime
    place: Place
    ayanamsa: Ayanamsa | None = None
    frame: ReferenceFrame = ReferenceFrame.GEOCENTRIC

    def __post_init__(self) -> None:
        if self.datetime.tzinfo is None:
            raise ValueError("ChartData.datetime must be timezone-aware")

    @property
    def utc(self) -> _datetime:
        """The `datetime` converted to UTC — convenience for calculations/serialization."""
        return self.datetime.astimezone(UTC)

    @property
    def jd(self) -> float:
        """Julian Day (UT) — what the ephemeris actually wants."""
        return julian_day(self.utc)

    @classmethod
    def from_iso(cls, iso: str, place: Place) -> ChartData:
        """Accept an ISO 8601 string like '1990-05-15T14:30:00-04:00'.

        The string must include a UTC offset or timezone designator.
        """
        return cls(datetime=_datetime.fromisoformat(iso), place=place)
