"""Dodecatemorion — twelfth-part transform, both Valens and Firmicus variants."""

from __future__ import annotations

import pytest

from astrologica.dodecatemorion import DodecatemorionVariant, compute_dodecatemorion

pytestmark = pytest.mark.pure


class TestDodecatemorionValens:
    """Valens formula: D(λ) = 30·sign + 12·(λ mod 30), mod 360."""

    @pytest.mark.parametrize(
        "longitude, expected",
        [
            (0.0, 0.0),  # 0° Aries → 0° Aries
            (10.0, 120.0),  # 10° Aries → 0° Leo (sign 4 × 30°)
            (30.0, 30.0),  # 0° Taurus → 0° Taurus
            (45.0, 210.0),  # 15° Taurus → 0° Scorpio (30 + 12*15 = 210)
            (29.999, 359.988),  # 29.999° Aries: 30*0 + 12*29.999 = 359.988
            (330.0, 330.0),  # 0° Pisces → 0° Pisces
        ],
    )
    def test_values(self, longitude: float, expected: float) -> None:
        assert float(
            compute_dodecatemorion(longitude, variant=DodecatemorionVariant.VALENS)
        ) == pytest.approx(expected, abs=1e-9)

    def test_default_variant_is_valens(self) -> None:
        # 10° Aries: Valens → 120°, Firmicus → 130°. Default must match Valens.
        assert float(compute_dodecatemorion(10.0)) == pytest.approx(120.0, abs=1e-9)


class TestDodecatemorionFirmicus:
    """Firmicus/Manilius formula: D(λ) = λ · 13, mod 360."""

    @pytest.mark.parametrize(
        "longitude, expected",
        [
            (0.0, 0.0),
            (10.0, 130.0),  # 10° Aries → 10° Leo
            (30.0, 30.0),  # 0° Taurus → 0° Taurus (matches Valens at sign boundary)
            (45.0, 225.0),  # 15° Taurus → 15° Scorpio
        ],
    )
    def test_values(self, longitude: float, expected: float) -> None:
        assert float(
            compute_dodecatemorion(longitude, variant=DodecatemorionVariant.FIRMICUS)
        ) == pytest.approx(expected, abs=1e-9)


class TestDodecatemorionAgreeAtSignBoundaries:
    """The two formulas only agree when `lon mod 30 == 0`."""

    @pytest.mark.parametrize("sign", list(range(12)))
    def test_agrees_at_each_sign_boundary(self, sign: int) -> None:
        lon = float(sign * 30)
        v = float(compute_dodecatemorion(lon, variant=DodecatemorionVariant.VALENS))
        f = float(compute_dodecatemorion(lon, variant=DodecatemorionVariant.FIRMICUS))
        assert v == pytest.approx(f, abs=1e-9)
