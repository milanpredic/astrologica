"""LotComponent — a symbolic point usable in a `CustomLot` formula.

The declarative DSL supports these component kinds (all are simple dataclasses
so the whole formula is JSON-serialisable):

- **Planet** (directly) — any enum member of `Planet`.
- **CardinalAngle(name)** — `ASC`, `MC`, `DSC`, `IC`.
- **HouseCusp(n)** — cusp of house n ∈ 1..12.
- **SyzygyPoint()** — the prenatal syzygy.
- **PriorLot(lot)** — any of the 7 classical lots already computed on the chart.
- **RulerOf(...)** — domicile ruler of a house or sign.
- **LordOf(kind)** — lord of the year/hour/day (Chaldean).

Resolution happens in `compute.py`, which turns each component into a
longitude at evaluation time.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union

from astrologica._internal.domain.lot.lot import Lot
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign


class CardinalAngleName(Enum):
    """One of the four primary chart angles."""

    ASC = "asc"
    MC = "mc"
    DSC = "dsc"
    IC = "ic"


@dataclass(frozen=True, slots=True)
class CardinalAngle:
    """One of ASC / MC / DSC / IC as a formula component."""

    angle: CardinalAngleName


@dataclass(frozen=True, slots=True)
class HouseCuspRef:
    """Reference to the cusp of house number `n` (1..12) in a chart.

    Named `HouseCuspRef` (not `HouseCusp`) to avoid colliding with the
    `HouseCusp` value object exported from `astrologica.house`.
    """

    n: int

    def __post_init__(self) -> None:
        if not 1 <= self.n <= 12:
            raise ValueError(f"house number must be in 1..12, got {self.n}")


@dataclass(frozen=True, slots=True)
class SyzygyPoint:
    """The prenatal syzygy longitude."""


@dataclass(frozen=True, slots=True)
class PriorLot:
    """A previously-computed classical lot (Fortune, Spirit, ...)."""

    lot: Lot


class RulerOfKind(Enum):
    HOUSE = "house"
    SIGN = "sign"


@dataclass(frozen=True, slots=True)
class RulerOf:
    """Domicile ruler of a house (by number) or a sign (by enum).

    Resolved via the chart's house cusps / the sign-rulership table.
    """

    kind: RulerOfKind
    house_n: int | None = None
    sign: Sign | None = None

    def __post_init__(self) -> None:
        if self.kind is RulerOfKind.HOUSE and self.house_n is None:
            raise ValueError("RulerOf(HOUSE) requires a house_n")
        if self.kind is RulerOfKind.SIGN and self.sign is None:
            raise ValueError("RulerOf(SIGN) requires a sign")


class LordKind(Enum):
    YEAR = "year"
    HOUR = "hour"
    DAY = "day"


@dataclass(frozen=True, slots=True)
class LordOf:
    """Lord of the year / hour / day (Chaldean association).

    Year: the sign Lord at the solar return. Hour: the current planetary hour's
    ruler. Day: the weekday's traditional ruler.
    """

    kind: LordKind


# Union of everything a formula may reference.
LotComponent = Union[
    Planet,
    CardinalAngle,
    HouseCuspRef,
    SyzygyPoint,
    PriorLot,
    RulerOf,
    LordOf,
]
