"""compute_dignities — the essential dignities a planet enjoys at a given longitude."""

from __future__ import annotations

from astrologica._internal.domain.dignity.dignity import Dignity
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign
from astrologica._internal.domain.tables.faces import face_of
from astrologica._internal.domain.tables.rulerships import DETRIMENT, DOMICILE, EXALTATION, FALL
from astrologica._internal.domain.tables.terms import TermsSystem, term_of
from astrologica._internal.domain.tables.triplicities import triplicity_of


def compute_dignities(
    planet: Planet,
    longitude: float,
    *,
    is_diurnal: bool = True,
    terms_system: TermsSystem = TermsSystem.EGYPTIAN,
) -> frozenset[Dignity]:
    """Return the set of essential dignities a planet has at the given longitude.

    `is_diurnal` switches the triplicity ruler between the day and night rulers.
    `terms_system` selects which of the five traditional bounds tables to use
    (default Egyptian — the Hellenistic standard).
    """
    sign = Sign.of(longitude)
    degree_in = Sign.degree_in(longitude)
    result: set[Dignity] = set()

    if DOMICILE.get(sign) is planet:
        result.add(Dignity.DOMICILE)
    if EXALTATION.get(sign) is planet:
        result.add(Dignity.EXALTATION)
    if DETRIMENT.get(sign) is planet:
        result.add(Dignity.DETRIMENT)
    if FALL.get(sign) is planet:
        result.add(Dignity.FALL)

    tri = triplicity_of(sign)
    if planet in (tri.day if is_diurnal else tri.night,):
        result.add(Dignity.TRIPLICITY)

    if term_of(sign, degree_in, system=terms_system) is planet:
        result.add(Dignity.TERM)
    if face_of(sign, degree_in) is planet:
        result.add(Dignity.FACE)

    return frozenset(result)
