"""Public facade for planet orientality (oriental/occidental of the Sun)."""

from astrologica._internal.domain.orientality.compute import planet_orientality
from astrologica._internal.domain.orientality.types import Orientality

__all__ = ["Orientality", "planet_orientality"]
