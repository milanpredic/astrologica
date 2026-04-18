"""Public facade for the Syzygy concept — event + kind enum + computation."""

from astrologica._internal.domain.syzygy import Syzygy, SyzygyKind
from astrologica._internal.domain.syzygy.compute import compute_prenatal_syzygy

__all__ = ["Syzygy", "SyzygyKind", "compute_prenatal_syzygy"]
