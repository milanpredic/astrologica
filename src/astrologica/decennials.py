"""Public facade for Decennials (Valens time-lord technique)."""

from astrologica._internal.domain.decennials import DecennialPeriod, compute_decennials

__all__ = ["DecennialPeriod", "compute_decennials"]
