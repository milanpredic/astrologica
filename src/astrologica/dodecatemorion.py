"""Public facade for the dodecatemorion (twelfth-part) transform."""

from astrologica._internal.domain.dodecatemorion import (
    DodecatemorionVariant,
    compute_dodecatemorion,
)

__all__ = ["DodecatemorionVariant", "compute_dodecatemorion"]
