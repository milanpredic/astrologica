"""Public facade for diurnal/nocturnal determination (traditional term: 'sect')."""

from astrologica._internal.domain.diurnal import compute_is_diurnal

__all__ = ["compute_is_diurnal"]
