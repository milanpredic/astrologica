"""compute_antiscion / compute_contraantiscion — pure longitude transforms.

Antiscion = mirror image of a point across the 0° Cancer / 0° Capricorn axis
(the solstitial axis). Contraantiscion = mirror across the 0° Aries / 0° Libra axis
(the equinoctial axis).
"""

from __future__ import annotations

from astrologica._internal.domain.measures.angle import Longitude, normalize_longitude


def compute_antiscion(longitude: Longitude | float) -> Longitude:
    """Return the antiscion (reflection through the solstitial axis)."""
    return Longitude(normalize_longitude(180.0 - float(longitude)))


def compute_contraantiscion(longitude: Longitude | float) -> Longitude:
    """Return the contraantiscion (reflection through the equinoctial axis)."""
    return Longitude(normalize_longitude(-float(longitude)))
