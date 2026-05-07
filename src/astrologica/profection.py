"""Public facade for annual profection (Ptolemaic 12-house cycle)."""

from astrologica._internal.domain.profection import (
    ProfectionPeriod,
    compute_annual_profection,
)

__all__ = ["ProfectionPeriod", "compute_annual_profection"]
