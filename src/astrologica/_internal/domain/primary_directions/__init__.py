"""Primary directions — Ptolemaic/Placidian promissor → significator arcs."""

from astrologica._internal.domain.primary_directions.approach import DirectionApproach
from astrologica._internal.domain.primary_directions.arc_key import ArcKey
from astrologica._internal.domain.primary_directions.compute import (
    PrimaryDirection,
    compute_primary_directions,
)
from astrologica._internal.domain.primary_directions.direction_type import DirectionType
from astrologica._internal.domain.primary_directions.speculum import (
    Speculum,
    compute_all_specula,
    compute_speculum,
)

__all__ = [
    "ArcKey",
    "DirectionApproach",
    "DirectionType",
    "PrimaryDirection",
    "Speculum",
    "compute_all_specula",
    "compute_primary_directions",
    "compute_speculum",
]
