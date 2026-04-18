"""House — the twelve houses, numbered 1..12."""

from __future__ import annotations

from enum import IntEnum


class House(IntEnum):
    """The twelve houses of the horoscope."""

    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7
    EIGHTH = 8
    NINTH = 9
    TENTH = 10
    ELEVENTH = 11
    TWELFTH = 12

    @property
    def is_angular(self) -> bool:
        return self in (House.FIRST, House.FOURTH, House.SEVENTH, House.TENTH)

    @property
    def is_succedent(self) -> bool:
        return self in (House.SECOND, House.FIFTH, House.EIGHTH, House.ELEVENTH)

    @property
    def is_cadent(self) -> bool:
        return self in (House.THIRD, House.SIXTH, House.NINTH, House.TWELFTH)
