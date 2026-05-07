"""House quality — angular / succedent / cadent classification."""

from __future__ import annotations

from enum import Enum

_ANGULAR = frozenset({1, 4, 7, 10})
_SUCCEDENT = frozenset({2, 5, 8, 11})
_CADENT = frozenset({3, 6, 9, 12})


class HouseQuality(Enum):
    """Traditional categorical strength of a house."""

    ANGULAR = "angular"
    SUCCEDENT = "succedent"
    CADENT = "cadent"


def house_quality(house_number: int) -> HouseQuality:
    """Classify a house as angular, succedent, or cadent.

    `house_number` must be in 1..12 inclusive. Raises ValueError otherwise.
    """
    if house_number in _ANGULAR:
        return HouseQuality.ANGULAR
    if house_number in _SUCCEDENT:
        return HouseQuality.SUCCEDENT
    if house_number in _CADENT:
        return HouseQuality.CADENT
    raise ValueError(f"house_number must be 1..12, got {house_number}")
