"""ArcKey — how to convert an arc of right ascension (degrees) into elapsed years.

Each "key" is a traditional rate at which the RA-arc separating promissor from
significator translates into physical time:

- `PTOLEMY` / `CARDAN`: one degree of RA = one year of life (simplest,
  astronomically crude).
- `NAIBOD`: the mean daily motion of the Sun (0.98565°/day) = one year — the
  most commonly used classical key.
- `TRUE_SOLAR_EQUATORIAL`: the Sun's actual RA motion on the native's birth
  day, used as the key. Unique per native.
- `BIRTHDAY_SOLAR_EQUATORIAL`: the Sun's actual RA motion averaged across the
  native's birth year, slightly different from `TRUE_SOLAR_EQUATORIAL`.
"""

from __future__ import annotations

from enum import Enum


class ArcKey(Enum):
    """Conversion rate from arc-in-RA to elapsed years."""

    PTOLEMY = "ptolemy"
    CARDAN = "cardan"
    NAIBOD = "naibod"
    TRUE_SOLAR_EQUATORIAL = "true_solar_equatorial"
    BIRTHDAY_SOLAR_EQUATORIAL = "birthday_solar_equatorial"
