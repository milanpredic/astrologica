"""Aspect concept — kind, endpoints (planet or angle), relation, computation, aversion."""

from astrologica._internal.domain.aspect.angle import Angle
from astrologica._internal.domain.aspect.aspect import Aspect, AspectEndpoint
from astrologica._internal.domain.aspect.aversion import is_in_aversion_to
from astrologica._internal.domain.aspect.kind import AspectKind

__all__ = ["Angle", "Aspect", "AspectEndpoint", "AspectKind", "is_in_aversion_to"]
