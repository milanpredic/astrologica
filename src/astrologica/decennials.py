"""Public facade for Decennials (Valens decennia time-lord technique)."""

from astrologica._internal.domain.decennials import (
    DecennialPeriod,
    DecennialSubPeriod,
    compute_decennials,
)

__all__ = ["DecennialPeriod", "DecennialSubPeriod", "compute_decennials"]
