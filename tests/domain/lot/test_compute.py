"""Hellenistic lot computation — day/night sensitivity and canonical formulae."""

from __future__ import annotations

import pytest

from astrologica._internal.domain.measures.angle import Latitude, Longitude
from astrologica._internal.domain.measures.ecliptic import EclipticPosition, Speed
from astrologica.lot import Lot, compute_lots
from astrologica.planet import Planet, PlanetPosition

pytestmark = pytest.mark.pure

# Canonical formulae:
#   FORTUNE    day: ASC + Moon    - Sun      night: ASC + Sun     - Moon
#   SPIRIT     day: ASC + Sun     - Moon     night: ASC + Moon    - Sun
#   EROS       day: ASC + Venus   - Spirit   night: ASC + Spirit  - Venus
#   NECESSITY  day: ASC + Fortune - Mercury  night: ASC + Mercury - Fortune
#   COURAGE    day: ASC + Fortune - Mars     night: ASC + Mars    - Fortune
#   VICTORY    day: ASC + Jupiter - Spirit   night: ASC + Spirit  - Jupiter
#   NEMESIS    day: ASC + Fortune - Saturn   night: ASC + Saturn  - Fortune


def _pp(planet: Planet, longitude: float) -> PlanetPosition:
    return PlanetPosition(
        planet=planet,
        position=EclipticPosition(
            longitude=Longitude(longitude),
            latitude=Latitude(0.0),
            speed=Speed(1.0),
        ),
    )


@pytest.fixture
def positions() -> dict[Planet, PlanetPosition]:
    return {
        Planet.SUN: _pp(Planet.SUN, 50.0),
        Planet.MOON: _pp(Planet.MOON, 100.0),
        Planet.MERCURY: _pp(Planet.MERCURY, 40.0),
        Planet.VENUS: _pp(Planet.VENUS, 70.0),
        Planet.MARS: _pp(Planet.MARS, 200.0),
        Planet.JUPITER: _pp(Planet.JUPITER, 300.0),
        Planet.SATURN: _pp(Planet.SATURN, 250.0),
    }


ASC = 10.0


def _norm(v: float) -> float:
    return v % 360.0


class TestFortune:
    def test_diurnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        # ASC + Moon - Sun = 10 + 100 - 50 = 60
        assert float(lots[Lot.FORTUNE].longitude) == pytest.approx(60.0)

    def test_nocturnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=False)
        # ASC + Sun - Moon = 10 + 50 - 100 = -40 → 320
        assert float(lots[Lot.FORTUNE].longitude) == pytest.approx(320.0)


class TestSpirit:
    def test_diurnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        # ASC + Sun - Moon = 10 + 50 - 100 = -40 → 320
        assert float(lots[Lot.SPIRIT].longitude) == pytest.approx(320.0)

    def test_nocturnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=False)
        # ASC + Moon - Sun = 60
        assert float(lots[Lot.SPIRIT].longitude) == pytest.approx(60.0)

    def test_spirit_and_fortune_reflect_across_asc(self, positions) -> None:
        """Spirit + Fortune = 2 × ASC (mod 360)."""
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        s = float(lots[Lot.SPIRIT].longitude)
        f = float(lots[Lot.FORTUNE].longitude)
        assert (s + f) % 360.0 == pytest.approx((2 * ASC) % 360.0)


class TestEros:
    def test_diurnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        spirit_d = 320.0
        expected = _norm(ASC + 70.0 - spirit_d)  # Venus - Spirit
        assert float(lots[Lot.EROS].longitude) == pytest.approx(expected)

    def test_nocturnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=False)
        spirit_n = 60.0
        expected = _norm(ASC + spirit_n - 70.0)  # Spirit - Venus
        assert float(lots[Lot.EROS].longitude) == pytest.approx(expected)


class TestNecessity:
    def test_diurnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        fortune_d = 60.0
        expected = _norm(ASC + fortune_d - 40.0)  # Fortune - Mercury
        assert float(lots[Lot.NECESSITY].longitude) == pytest.approx(expected)

    def test_nocturnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=False)
        fortune_n = 320.0
        expected = _norm(ASC + 40.0 - fortune_n)  # Mercury - Fortune
        assert float(lots[Lot.NECESSITY].longitude) == pytest.approx(expected)


class TestCourage:
    def test_diurnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        fortune_d = 60.0
        expected = _norm(ASC + fortune_d - 200.0)  # Fortune - Mars
        assert float(lots[Lot.COURAGE].longitude) == pytest.approx(expected)

    def test_nocturnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=False)
        fortune_n = 320.0
        expected = _norm(ASC + 200.0 - fortune_n)  # Mars - Fortune
        assert float(lots[Lot.COURAGE].longitude) == pytest.approx(expected)


class TestVictory:
    def test_diurnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        spirit_d = 320.0
        expected = _norm(ASC + 300.0 - spirit_d)  # Jupiter - Spirit
        assert float(lots[Lot.VICTORY].longitude) == pytest.approx(expected)

    def test_nocturnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=False)
        spirit_n = 60.0
        expected = _norm(ASC + spirit_n - 300.0)  # Spirit - Jupiter
        assert float(lots[Lot.VICTORY].longitude) == pytest.approx(expected)


class TestNemesis:
    def test_diurnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        fortune_d = 60.0
        expected = _norm(ASC + fortune_d - 250.0)  # Fortune - Saturn
        assert float(lots[Lot.NEMESIS].longitude) == pytest.approx(expected)

    def test_nocturnal(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=False)
        fortune_n = 320.0
        expected = _norm(ASC + 250.0 - fortune_n)  # Saturn - Fortune
        assert float(lots[Lot.NEMESIS].longitude) == pytest.approx(expected)


class TestAllSevenLots:
    def test_returns_all_seven(self, positions) -> None:
        lots = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        assert set(lots.keys()) == set(Lot)

    def test_sect_inversion_changes_derived_lots(self, positions) -> None:
        """Sect inversion produces different outputs for every lot. (The
        simple reflection-across-ASC identity only holds for Fortune and
        Spirit, not derived lots whose formulas reference other lots.)"""
        day = compute_lots(positions, ascendant=ASC, is_diurnal=True)
        night = compute_lots(positions, ascendant=ASC, is_diurnal=False)
        for lot in Lot:
            d = float(day[lot].longitude)
            n = float(night[lot].longitude)
            assert d != n, f"{lot.name} should differ between day and night"
