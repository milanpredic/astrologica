"""LotFormula — a pair of (plus, minus) component lists.

The formula body is `ASC + Σplus − Σminus`. `ASC` is always the base point
(the convention for every traditional Hellenistic / Arabic lot), so callers
only specify the non-ASC parts.
"""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.custom_lot.component import LotComponent


@dataclass(frozen=True, slots=True)
class LotFormula:
    """One of the two half-formulas (day or night) for a custom lot."""

    plus: tuple[LotComponent, ...]
    minus: tuple[LotComponent, ...]
