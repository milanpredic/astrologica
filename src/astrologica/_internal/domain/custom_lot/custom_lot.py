"""CustomLot — a user-defined lot with day/night formulas."""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.custom_lot.formula import LotFormula


@dataclass(frozen=True, slots=True)
class CustomLot:
    """A custom lot definition: name + day formula + night formula."""

    name: str
    day: LotFormula
    night: LotFormula
