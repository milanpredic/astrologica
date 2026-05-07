"""Public-facade smoke test for astrologica.triplicities."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from astrologica import Planet, Sign

pytestmark = pytest.mark.pure


def test_triplicity_of_aries_returns_dorothean_fire_rulers() -> None:
    from astrologica.triplicities import triplicity_of

    rulers = triplicity_of(Sign.ARIES)
    assert rulers.day is Planet.SUN
    assert rulers.night is Planet.JUPITER
    assert rulers.participating is Planet.SATURN


def test_triplicity_table_covers_all_four_elements() -> None:
    from astrologica._internal.domain.sign import Element
    from astrologica.triplicities import TRIPLICITY_BY_ELEMENT

    assert set(TRIPLICITY_BY_ELEMENT.keys()) == set(Element)


def test_triplicity_rulers_dataclass_is_frozen() -> None:
    from astrologica.triplicities import TriplicityRulers

    rulers = TriplicityRulers(day=Planet.SUN, night=Planet.MOON, participating=Planet.MARS)
    with pytest.raises(FrozenInstanceError):
        rulers.day = Planet.VENUS  # type: ignore[misc]
