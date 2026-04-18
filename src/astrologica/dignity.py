"""Public facade for the Dignity enum + essential-dignity lookup."""

from astrologica._internal.domain.dignity import Dignity
from astrologica._internal.domain.dignity.compute import compute_dignities
from astrologica._internal.domain.tables.terms import TermsSystem

__all__ = ["Dignity", "TermsSystem", "compute_dignities"]
