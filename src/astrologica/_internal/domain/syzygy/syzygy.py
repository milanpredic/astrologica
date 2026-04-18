"""Syzygy — the prenatal lunation event (last new or full moon before birth)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from astrologica._internal.domain.measures.angle import Longitude
from astrologica._internal.domain.sign import Sign
from astrologica._internal.domain.syzygy.kind import SyzygyKind


@dataclass(frozen=True, slots=True)
class Syzygy:
    """Prenatal lunation: time, kind (new/full), and the conjoining/opposing longitude.

    For a new moon: Sun and Moon are at the same longitude (stored in `longitude`).
    For a full moon: the Moon is opposite the Sun; `longitude` holds the Moon's position.
    """

    kind: SyzygyKind
    when: datetime
    longitude: Longitude

    @property
    def sign(self) -> Sign:
        return Sign.of(self.longitude)
