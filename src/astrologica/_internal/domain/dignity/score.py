"""Lilly-style numeric dignity scoring.

Sum the weights of each dignity a planet holds at a longitude. Triplicity
respects the diurnal/nocturnal sect. Detriment and fall add their (negative)
weights.

Adapted from old_projects/morinus-console/almutens.py:170-249 (per-dignity
scoring inside Essentials.getData). Default weights are Lilly's classical
+5/+4/+3/+2/+1, -5/-4 — apps wanting a different scheme pass their own
EssentialWeights.
"""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign
from astrologica._internal.domain.tables.faces import face_of
from astrologica._internal.domain.tables.rulerships import DETRIMENT, DOMICILE, EXALTATION, FALL
from astrologica._internal.domain.tables.terms import TermsSystem, term_of
from astrologica._internal.domain.tables.triplicities import triplicity_of


@dataclass(frozen=True, slots=True)
class EssentialWeights:
    """Numeric weights for the seven essential-dignity categories."""

    domicile: int
    exaltation: int
    triplicity: int
    term: int
    face: int
    detriment: int
    fall: int


LILLY_WEIGHTS: EssentialWeights = EssentialWeights(
    domicile=5,
    exaltation=4,
    triplicity=3,
    term=2,
    face=1,
    detriment=-5,
    fall=-4,
)


def dignity_score(
    planet: Planet,
    longitude: float,
    *,
    is_diurnal: bool,
    weights: EssentialWeights = LILLY_WEIGHTS,
    terms_system: TermsSystem = TermsSystem.EGYPTIAN,
) -> int:
    """Sum the dignity weights `planet` earns at `longitude`.

    `is_diurnal` switches the triplicity ruler between day and night.
    `terms_system` selects which bounds table to use (default Egyptian).
    """
    sign = Sign.of(longitude)
    degree_in = Sign.degree_in(longitude)
    score = 0

    if DOMICILE.get(sign) is planet:
        score += weights.domicile
    if EXALTATION.get(sign) is planet:
        score += weights.exaltation
    if DETRIMENT.get(sign) is planet:
        score += weights.detriment
    if FALL.get(sign) is planet:
        score += weights.fall

    tri = triplicity_of(sign)
    if (tri.day if is_diurnal else tri.night) is planet:
        score += weights.triplicity

    if term_of(sign, degree_in, system=terms_system) is planet:
        score += weights.term
    if face_of(sign, degree_in) is planet:
        score += weights.face

    return score
