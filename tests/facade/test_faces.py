"""Public-facade smoke test for astrologica.faces."""

from __future__ import annotations

import pytest

from astrologica import Planet, Sign

pytestmark = pytest.mark.pure


def test_face_of_first_decan_aries_is_mars() -> None:
    from astrologica.faces import face_of

    assert face_of(Sign.ARIES, 0.0) is Planet.MARS


def test_face_of_second_decan_aries_is_sun() -> None:
    from astrologica.faces import face_of

    assert face_of(Sign.ARIES, 15.0) is Planet.SUN


def test_FACES_table_has_three_decans_per_sign() -> None:
    from astrologica.faces import FACES

    for sign in Sign:
        assert len(FACES[sign]) == 3
        for ruler in FACES[sign]:
            assert isinstance(ruler, Planet)
