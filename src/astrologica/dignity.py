"""Public facade for the Dignity enum + essential-dignity lookup + numeric scoring."""

from astrologica._internal.domain.dignity import Dignity
from astrologica._internal.domain.dignity.compute import compute_dignities
from astrologica._internal.domain.dignity.score import (
    LILLY_WEIGHTS,
    EssentialWeights,
    dignity_score,
)
from astrologica._internal.domain.tables.terms import TermsSystem

__all__ = [
    "Dignity",
    "EssentialWeights",
    "LILLY_WEIGHTS",
    "TermsSystem",
    "compute_dignities",
    "dignity_score",
]
