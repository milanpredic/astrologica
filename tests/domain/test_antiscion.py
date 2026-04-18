"""Antiscion + contraantiscion — pure longitude transforms."""

from __future__ import annotations

import pytest

from astrologica.antiscion import compute_antiscion, compute_contraantiscion

pytestmark = pytest.mark.pure


class TestAntiscion:
    @pytest.mark.parametrize(
        "longitude, expected",
        [
            # Solstitial axis: 0° Cancer (= 90°) and 0° Capricorn (= 270°) are their own antiscia.
            (90.0, 90.0),
            (270.0, 270.0),
            # 0° Aries (0°) mirrors to 0° Virgo (150° -> wait, 180 - 0 = 180 ... that's Libra 0°).
            # Let me recompute: 180 - 0 = 180 (0° Libra). Actually the Valens convention:
            # antiscion of 0° Aries is 0° Virgo (150°). But that's a different mirror axis.
            # Our formula uses the solstitial axis (Cancer/Capricorn): mirrored around 90°/270°.
            # Mirror of 0° Aries (0°) across 90° axis = 180° (0° Libra). Actually traditionally,
            # antiscion mirrors across 0° Cancer / 0° Capricorn, so:
            #   15° Gemini (75°) <-> 15° Cancer (105°)  (reflection around the 90° solstice)
            # But a simpler equivalent definition: antiscion = 180 - longitude (mod 360).
            # So 0° Aries (0°) -> 180° (0° Libra). That's the equinoctial axis mirror.
            # The difference between antiscion and contraantiscion is exactly which axis.
            # We follow the convention: antiscion = solstitial axis (Cancer/Capricorn):
            #   antiscion(lon) = (180 - lon) mod 360
            # and contraantiscion = equinoctial axis (Aries/Libra):
            #   contraantiscion(lon) = (-lon) mod 360
            (15.0, 165.0),  # 15° Aries -> 15° Virgo
            (75.0, 105.0),  # 15° Gemini -> 15° Cancer
            (285.0, 255.0),  # 15° Aquarius -> 15° Sagittarius
        ],
    )
    def test_values(self, longitude: float, expected: float) -> None:
        result = float(compute_antiscion(longitude))
        assert result == pytest.approx(expected, abs=1e-9)

    def test_is_involution(self) -> None:
        """Applying antiscion twice returns the original."""
        assert float(compute_antiscion(float(compute_antiscion(42.5)))) == pytest.approx(42.5)


class TestContraAntiscion:
    @pytest.mark.parametrize(
        "longitude, expected",
        [
            (0.0, 0.0),  # 0° Aries -> itself (on equinoctial axis)
            (180.0, 180.0),  # 0° Libra -> itself
            (15.0, 345.0),  # 15° Aries -> 15° Pisces
            (90.0, 270.0),  # 0° Cancer -> 0° Capricorn
        ],
    )
    def test_values(self, longitude: float, expected: float) -> None:
        assert float(compute_contraantiscion(longitude)) == pytest.approx(expected, abs=1e-9)

    def test_is_involution(self) -> None:
        assert float(
            compute_contraantiscion(float(compute_contraantiscion(200.0)))
        ) == pytest.approx(200.0)
