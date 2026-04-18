"""Essential-dignity lookup — known canonical placements."""

from __future__ import annotations

import pytest

from astrologica.dignity import Dignity, compute_dignities
from astrologica.planet import Planet

pytestmark = pytest.mark.pure


class TestDignities:
    def test_sun_in_leo_is_domicile(self) -> None:
        d = compute_dignities(Planet.SUN, 130.0)  # 10° Leo
        assert Dignity.DOMICILE in d

    def test_sun_in_aries_is_exalted(self) -> None:
        d = compute_dignities(Planet.SUN, 19.0)  # 19° Aries (exaltation degree is 19)
        assert Dignity.EXALTATION in d

    def test_sun_in_aquarius_is_in_detriment(self) -> None:
        # Sun rules Leo → detriment in Aquarius (5×30 + 30 = 300°-330°).
        d = compute_dignities(Planet.SUN, 310.0)
        assert Dignity.DETRIMENT in d

    def test_sun_in_libra_is_in_fall(self) -> None:
        # Sun is exalted in Aries → fall in Libra.
        d = compute_dignities(Planet.SUN, 190.0)
        assert Dignity.FALL in d

    def test_mars_in_aries_domicile_and_first_term(self) -> None:
        # 0..6° Aries: Egyptian term of Jupiter. 6..12° Aries: term of Venus.
        d_at_5 = compute_dignities(Planet.MARS, 5.0)
        assert Dignity.DOMICILE in d_at_5
        assert Dignity.TERM not in d_at_5  # Jupiter rules 0..6° term

        d_at_22 = compute_dignities(Planet.MARS, 22.0)  # 22° Aries — Mars term 20..25°
        assert Dignity.DOMICILE in d_at_22
        assert Dignity.TERM in d_at_22

    def test_triplicity_swaps_with_sect(self) -> None:
        # Fire element: day ruler = Sun, night ruler = Jupiter.
        # Sun in Leo (fire sign) has triplicity by day only.
        day = compute_dignities(Planet.SUN, 130.0, is_diurnal=True)
        night = compute_dignities(Planet.SUN, 130.0, is_diurnal=False)
        assert Dignity.TRIPLICITY in day
        assert Dignity.TRIPLICITY not in night

    def test_face_mars_aries_0_to_10(self) -> None:
        d = compute_dignities(Planet.MARS, 5.0)  # 5° Aries — Mars face
        assert Dignity.FACE in d
