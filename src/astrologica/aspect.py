"""Public facade for the Aspect concept — kind, endpoints, computation, orbs, aversion."""

from astrologica._internal.domain.aspect import (
    Angle,
    Aspect,
    AspectEndpoint,
    AspectKind,
    is_in_aversion_to,
)
from astrologica._internal.domain.aspect.compute import compute_aspects
from astrologica._internal.domain.tables.aspect_angles import (
    DEFAULT_ORBS,
    LUMINARY_ORB_BONUS,
    default_orb,
)

__all__ = [
    "Angle",
    "Aspect",
    "AspectEndpoint",
    "AspectKind",
    "DEFAULT_ORBS",
    "LUMINARY_ORB_BONUS",
    "compute_aspects",
    "default_orb",
    "is_in_aversion_to",
]
