"""Public facade for term distribution under primary direction of the Ascendant."""

from astrologica._internal.domain.term_distribution import (
    TermPeriod,
    compute_term_distribution,
)

__all__ = ["TermPeriod", "compute_term_distribution"]
