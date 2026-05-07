"""Public facade for the Dorothean triplicity rulership table."""

from astrologica._internal.domain.tables.triplicities import (
    TRIPLICITY_BY_ELEMENT,
    TriplicityRulers,
    triplicity_of,
)

__all__ = ["TRIPLICITY_BY_ELEMENT", "TriplicityRulers", "triplicity_of"]
