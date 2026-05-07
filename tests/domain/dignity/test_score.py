"""dignity_score — Lilly numeric scoring of essential dignities."""

from __future__ import annotations

import pytest

from astrologica import Planet, TermsSystem

pytestmark = pytest.mark.pure


def test_planet_in_own_domicile_scores_at_least_5() -> None:
    """Mars at 0° Aries: domicile (+5) at minimum."""
    from astrologica._internal.domain.dignity.score import LILLY_WEIGHTS, dignity_score

    score = dignity_score(Planet.MARS, 0.0, is_diurnal=True, weights=LILLY_WEIGHTS)
    # Domicile +5; face at Aries 0° is Mars (+1); term at Aries 0° is Jupiter (no);
    # triplicity (Fire/diurnal) is Sun (no). So minimum is 5+1 = 6.
    assert score == 6


def test_planet_in_detriment_scores_at_most_negative_5() -> None:
    """Mars in Libra: detriment (-5)."""
    from astrologica._internal.domain.dignity.score import LILLY_WEIGHTS, dignity_score

    score = dignity_score(Planet.MARS, 180.0 + 22.0, is_diurnal=True, weights=LILLY_WEIGHTS)
    assert score <= -5


def test_planet_outside_all_dignities_scores_zero() -> None:
    """Saturn at 0° Sagittarius: no Saturn dignity (Sag is Jupiter's domicile;
    fire-diurnal triplicity is Sun; term is Jupiter; face is Mercury)."""
    from astrologica._internal.domain.dignity.score import LILLY_WEIGHTS, dignity_score

    score = dignity_score(Planet.SATURN, 240.0, is_diurnal=True, weights=LILLY_WEIGHTS)
    assert score == 0


def test_lilly_weights_default_values() -> None:
    from astrologica._internal.domain.dignity.score import LILLY_WEIGHTS

    assert LILLY_WEIGHTS.domicile == 5
    assert LILLY_WEIGHTS.exaltation == 4
    assert LILLY_WEIGHTS.triplicity == 3
    assert LILLY_WEIGHTS.term == 2
    assert LILLY_WEIGHTS.face == 1
    assert LILLY_WEIGHTS.detriment == -5
    assert LILLY_WEIGHTS.fall == -4


def test_dignity_score_respects_custom_weights() -> None:
    """Override weights: give domicile a much larger bonus."""
    from astrologica._internal.domain.dignity.score import EssentialWeights, dignity_score

    custom = EssentialWeights(
        domicile=10, exaltation=8, triplicity=6, term=4, face=2, detriment=-20, fall=-10
    )
    # Mars at 0° Aries with custom weights: domicile +10 + face +2 = 12.
    score = dignity_score(Planet.MARS, 0.0, is_diurnal=True, weights=custom)
    assert score == 12


def test_dignity_score_terms_system_changes_term_owner() -> None:
    """Different terms systems may attribute the term to a different planet."""
    from astrologica._internal.domain.dignity.score import LILLY_WEIGHTS, dignity_score

    venus_egy = dignity_score(
        Planet.VENUS,
        8.0,
        is_diurnal=True,
        weights=LILLY_WEIGHTS,
        terms_system=TermsSystem.EGYPTIAN,
    )
    venus_pto = dignity_score(
        Planet.VENUS,
        8.0,
        is_diurnal=True,
        weights=LILLY_WEIGHTS,
        terms_system=TermsSystem.PTOLEMAIC,
    )
    # Both systems give Venus the term at this longitude.
    assert venus_egy == venus_pto
