"""Planet orientality classification — oriental / occidental / neutral of the Sun.

The package exposes only the type from `__init__` to avoid an import cycle
with `planet.position` (which embeds `Orientality` as a field). Consumers of
the function `planet_orientality` import from the `compute` submodule.
"""

from astrologica._internal.domain.orientality.types import Orientality

__all__ = ["Orientality"]
