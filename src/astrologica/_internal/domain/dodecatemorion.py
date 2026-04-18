"""compute_dodecatemorion — the traditional twelfth-part of a longitude.

Two traditions disagree on the formula. For a longitude λ = 30·s + r
(where `s` is the sign index 0..11 and `r` is the degrees-in-sign 0..30):

- `VALENS` tradition (Vettius Valens, Anthology IX.21):
      `D(λ) = 30·s + 12·r` (mod 360)
  Amplifies the in-sign degree by 12 within the zodiacal frame. At a sign
  boundary (r = 0) it collapses to the sign itself.

- `FIRMICUS` tradition (also attributed to Manilius and some later Arabic
  sources):
      `D(λ) = λ · 13` (mod 360)
  Slightly different: adds the original degree back in, so even 10° Aries
  lands at 10° Leo rather than 0° Leo.

The two agree only when the longitude falls exactly on a sign boundary
(`r == 0`). `DodecatemorionVariant.VALENS` is the default; it matches the
library's namesake source.
"""

from __future__ import annotations

from enum import Enum

from astrologica._internal.domain.measures.angle import Longitude, normalize_longitude


class DodecatemorionVariant(Enum):
    """Which of the two classical formulas to apply."""

    VALENS = "valens"
    FIRMICUS = "firmicus"


def compute_dodecatemorion(
    longitude: Longitude | float,
    variant: DodecatemorionVariant = DodecatemorionVariant.VALENS,
) -> Longitude:
    """Return the dodecatemorion (twelfth-part) of a longitude.

    For `λ = 10° Aries`:
    - `VALENS` (default) → `0° Leo` (120°)
    - `FIRMICUS` → `10° Leo` (130°)
    """
    lon = float(longitude)
    if variant is DodecatemorionVariant.VALENS:
        sign = int(lon // 30.0) % 12
        r = lon - (sign * 30.0)
        value = 30.0 * sign + 12.0 * r
    else:  # FIRMICUS
        value = lon * 13.0
    return Longitude(normalize_longitude(value))
