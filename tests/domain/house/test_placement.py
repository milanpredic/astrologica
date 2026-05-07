"""house_of — locate which 1..12 house a longitude falls in, given cusps."""

from __future__ import annotations

from astrologica._internal.domain.house.cusp import HouseCusp
from astrologica._internal.domain.house.house import House
from astrologica._internal.domain.house.placement import house_of
from astrologica._internal.domain.measures.angle import Longitude


def _whole_sign_cusps(asc_lon: float) -> tuple[HouseCusp, ...]:
    """Build whole-sign cusps starting at the sign of `asc_lon`."""
    asc_sign_start = (asc_lon // 30.0) * 30.0
    return tuple(
        HouseCusp(house=House(i + 1), cusp=Longitude((asc_sign_start + i * 30.0) % 360.0))
        for i in range(12)
    )


class TestWholeSignPlacement:
    def test_position_in_first_house(self) -> None:
        cusps = _whole_sign_cusps(asc_lon=15.0)  # ASC in Aries
        # 5° in Aries → 1st house.
        assert house_of(5.0, cusps) == 1

    def test_position_in_seventh_house(self) -> None:
        cusps = _whole_sign_cusps(asc_lon=15.0)  # ASC in Aries → 7th in Libra (180°)
        assert house_of(195.0, cusps) == 7

    def test_position_just_below_first_cusp_is_twelfth(self) -> None:
        cusps = _whole_sign_cusps(
            asc_lon=15.0
        )  # 1st cusp at 0° Aries; 12th cusp at 0° Pisces (330°)
        # 359.99° (Pisces 29°59') is in the 12th.
        assert house_of(359.99, cusps) == 12


class TestWrapAround:
    def test_handles_zero_crossing(self) -> None:
        # ASC just past 0° Aries; 12th cusp at 0° Pisces (330°). Any longitude in
        # 330..360 should land in the 12th house.
        cusps = _whole_sign_cusps(asc_lon=5.0)
        assert house_of(330.0, cusps) == 12
        assert house_of(355.0, cusps) == 12
        assert house_of(0.5, cusps) == 1


class TestEmptyCusps:
    def test_empty_cusps_returns_none(self) -> None:
        assert house_of(180.0, ()) is None
