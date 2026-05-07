"""Term distribution — sequence of term-rulers under primary direction of the Ascendant."""

from astrologica._internal.domain.term_distribution.compute import compute_term_distribution
from astrologica._internal.domain.term_distribution.types import TermPeriod

__all__ = ["TermPeriod", "compute_term_distribution"]
