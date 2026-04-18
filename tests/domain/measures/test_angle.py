"""Angle primitives — normalisation, comparison, arc."""

from __future__ import annotations

import pytest

from astrologica.angle import Degree, Latitude, Longitude, Orb, normalize_longitude, shortest_arc

pytestmark = pytest.mark.pure


class TestLongitude:
    def test_normalises_into_zero_to_360(self) -> None:
        assert Longitude(370.0).value == pytest.approx(10.0)
        assert Longitude(-10.0).value == pytest.approx(350.0)
        assert Longitude(0.0).value == 0.0

    def test_arc_to_handles_wrap(self) -> None:
        a = Longitude(350.0)
        b = Longitude(10.0)
        # shortest arc from 350 → 10 is +20°, not -340°.
        assert a.arc_to(b) == pytest.approx(20.0)
        assert b.arc_to(a) == pytest.approx(-20.0)


class TestLatitude:
    def test_rejects_out_of_range(self) -> None:
        with pytest.raises(ValueError):
            Latitude(91.0)
        with pytest.raises(ValueError):
            Latitude(-90.01)

    def test_accepts_boundaries(self) -> None:
        assert Latitude(90.0).value == 90.0
        assert Latitude(-90.0).value == -90.0


class TestOrb:
    def test_rejects_negative(self) -> None:
        with pytest.raises(ValueError):
            Orb(-0.01)

    def test_zero_allowed(self) -> None:
        assert Orb(0.0).value == 0.0


class TestDegree:
    def test_is_a_float_wrapper(self) -> None:
        assert float(Degree(5.5)) == 5.5


class TestNormalize:
    def test_equivalence(self) -> None:
        assert normalize_longitude(720.0) == pytest.approx(0.0)
        assert normalize_longitude(-359.9) == pytest.approx(0.1)


class TestShortestArc:
    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (0.0, 90.0, 90.0),
            (350.0, 10.0, 20.0),
            (10.0, 350.0, -20.0),
            (0.0, 180.0, 180.0),
            (0.0, 181.0, -179.0),
        ],
    )
    def test_values(self, a: float, b: float, expected: float) -> None:
        assert shortest_arc(a, b) == pytest.approx(expected)
