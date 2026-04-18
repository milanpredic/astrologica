"""Sign — the twelve zodiac signs + element/modality/ruler metadata."""

from __future__ import annotations

from enum import IntEnum

from astrologica._internal.domain.measures.angle import Longitude


class Element(IntEnum):
    FIRE = 0
    EARTH = 1
    AIR = 2
    WATER = 3


class Modality(IntEnum):
    CARDINAL = 0
    FIXED = 1
    MUTABLE = 2


class Sign(IntEnum):
    """The twelve zodiac signs, ordered from 0° Aries. Values are 0..11."""

    ARIES = 0
    TAURUS = 1
    GEMINI = 2
    CANCER = 3
    LEO = 4
    VIRGO = 5
    LIBRA = 6
    SCORPIO = 7
    SAGITTARIUS = 8
    CAPRICORN = 9
    AQUARIUS = 10
    PISCES = 11

    @property
    def element(self) -> Element:
        return _ELEMENT_BY_SIGN[self]

    @property
    def modality(self) -> Modality:
        return _MODALITY_BY_SIGN[self]

    @property
    def start_longitude(self) -> float:
        """Longitude (degrees) where this sign begins (0° Aries = 0°)."""
        return float(self.value) * 30.0

    @classmethod
    def of(cls, longitude: Longitude | float) -> Sign:
        """Sign containing the given ecliptic longitude."""
        lon = float(longitude) % 360.0
        return cls(int(lon // 30))

    @classmethod
    def degree_in(cls, longitude: Longitude | float) -> float:
        """Degree within the sign (0..30) for the given longitude."""
        return float(longitude) % 30.0


_ELEMENT_BY_SIGN: dict[Sign, Element] = {
    Sign.ARIES: Element.FIRE,
    Sign.TAURUS: Element.EARTH,
    Sign.GEMINI: Element.AIR,
    Sign.CANCER: Element.WATER,
    Sign.LEO: Element.FIRE,
    Sign.VIRGO: Element.EARTH,
    Sign.LIBRA: Element.AIR,
    Sign.SCORPIO: Element.WATER,
    Sign.SAGITTARIUS: Element.FIRE,
    Sign.CAPRICORN: Element.EARTH,
    Sign.AQUARIUS: Element.AIR,
    Sign.PISCES: Element.WATER,
}

_MODALITY_BY_SIGN: dict[Sign, Modality] = {
    Sign.ARIES: Modality.CARDINAL,
    Sign.TAURUS: Modality.FIXED,
    Sign.GEMINI: Modality.MUTABLE,
    Sign.CANCER: Modality.CARDINAL,
    Sign.LEO: Modality.FIXED,
    Sign.VIRGO: Modality.MUTABLE,
    Sign.LIBRA: Modality.CARDINAL,
    Sign.SCORPIO: Modality.FIXED,
    Sign.SAGITTARIUS: Modality.MUTABLE,
    Sign.CAPRICORN: Modality.CARDINAL,
    Sign.AQUARIUS: Modality.FIXED,
    Sign.PISCES: Modality.MUTABLE,
}
