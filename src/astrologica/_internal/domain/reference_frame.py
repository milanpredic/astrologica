"""ReferenceFrame — observer frame used for body positions.

Three frames are supported:

- `GEOCENTRIC` (default, traditional astrology): positions as seen from Earth's
  centre. This is what every published almanac and traditional astrology text
  refers to.
- `TOPOCENTRIC`: corrected for the observer's location on Earth's surface
  (parallax). Differs from geocentric by up to ~1° for the Moon near the horizon,
  much less for everything else. Occasionally used for eclipse / occultation work.
- `HELIOCENTRIC`: as seen from the Sun. Research / theoretical tool; makes the
  Earth a "planet" (at opposition to the geocentric Sun) and collapses the Sun
  to ~0° longitude.
"""

from __future__ import annotations

from enum import Enum


class ReferenceFrame(Enum):
    """Observer frame for body positions."""

    GEOCENTRIC = "geocentric"
    TOPOCENTRIC = "topocentric"
    HELIOCENTRIC = "heliocentric"
