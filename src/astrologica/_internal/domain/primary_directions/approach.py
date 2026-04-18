"""DirectionApproach — zodiacal vs mundane primary directions.

Both approaches answer "when does promissor reach the aspect of significator?"
but measure the arc differently:

- **ZODIACAL**: the promissor is directed to the ecliptic degree where it
  forms the aspect. Arc is the RA-difference between that degree's right
  ascension and the significator's RA, corrected by the ascensional
  difference at the significator's pole (Placidian semi-arc).
- **MUNDANE**: the promissor is directed through mundane houses. Arc is the
  difference in Placidian mundane position (PMP) between promissor and
  significator, scaled by the significator's semi-arc.
"""

from __future__ import annotations

from enum import Enum


class DirectionApproach(Enum):
    ZODIACAL = "zodiacal"
    MUNDANE = "mundane"
