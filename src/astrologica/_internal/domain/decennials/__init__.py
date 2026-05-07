"""Decennials (Valens) — sect-conditional time-lord technique.

Each of the seven classical planets rules a major period of years; the
sequence starts with the sect light (Sun for diurnal, Moon for nocturnal)
and proceeds in Chaldean order. Total cycle length is 126 years (the "Mu"
cycle).

Period lengths (per Valens):
  Sun=19 / Venus=8 / Mercury=20 / Moon=25 / Saturn=27 / Jupiter=12 / Mars=15
"""

from astrologica._internal.domain.decennials.compute import compute_decennials
from astrologica._internal.domain.decennials.types import DecennialPeriod

__all__ = ["DecennialPeriod", "compute_decennials"]
