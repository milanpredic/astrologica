"""Public facade for the Aspect concept — kind enum + relation object + computation."""

from astrologica._internal.domain.aspect import Aspect, AspectKind
from astrologica._internal.domain.aspect.compute import compute_aspects

__all__ = ["Aspect", "AspectKind", "compute_aspects"]
