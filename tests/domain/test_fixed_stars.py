"""Fixed stars — conjunctions between chart bodies and the 30 classical stars."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica.chart import compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.fixed_stars import FixedStar, compute_fixed_star_conjunctions
from astrologica.place import Place
from astrologica.planet import Planet
from tests.fakes.fake_ephemeris import FakeEphemeris


@pytest.mark.pure
class TestFixedStarEnum:
    def test_has_thirty_members(self) -> None:
        assert len(list(FixedStar)) == 30

    def test_valens_canonical_stars_present(self) -> None:
        names = {s.name for s in FixedStar}
        for required in (
            "ALDEBARAN",
            "ANTARES",
            "REGULUS",
            "SPICA",
            "SIRIUS",
            "FOMALHAUT",
            "BETELGEUSE",
            "POLLUX",
            "VEGA",
            "ARCTURUS",
        ):
            assert required in names


@pytest.mark.infrastructure
class TestFixedStarRealPositions:
    """Real Swiss Ephemeris positions for well-known stars at J2000.

    `sefstars.txt` is bundled with the package under `astrologica/_data/`
    so these tests pass without any external data-file install.
    """

    def test_regulus_longitude_near_end_of_leo_at_j2000(self) -> None:
        """Regulus at J2000.0 ≈ 29°50′ Leo ≈ 149.83° tropical."""
        from astrologica._internal.domain.measures.jd import julian_day
        from astrologica.swisseph import SwissEphemerisAdapter

        jd = julian_day(datetime(2000, 1, 1, 12, 0, tzinfo=UTC))
        adapter = SwissEphemerisAdapter()
        lon = adapter.fixed_star_longitude("regulus", jd)
        assert 149.5 < lon < 150.1

    def test_aldebaran_longitude_at_j2000(self) -> None:
        """Aldebaran at J2000.0 ≈ 9°47′ Gemini ≈ 69.78° tropical."""
        from astrologica._internal.domain.measures.jd import julian_day
        from astrologica.swisseph import SwissEphemerisAdapter

        jd = julian_day(datetime(2000, 1, 1, 12, 0, tzinfo=UTC))
        adapter = SwissEphemerisAdapter()
        lon = adapter.fixed_star_longitude("aldebaran", jd)
        assert 69.5 < lon < 70.1

    def test_spica_longitude_at_j2000(self) -> None:
        """Spica at J2000.0 ≈ 23°50′ Libra ≈ 203.83° tropical."""
        from astrologica._internal.domain.measures.jd import julian_day
        from astrologica.swisseph import SwissEphemerisAdapter

        jd = julian_day(datetime(2000, 1, 1, 12, 0, tzinfo=UTC))
        adapter = SwissEphemerisAdapter()
        lon = adapter.fixed_star_longitude("spica", jd)
        assert 203.5 < lon < 204.1


@pytest.mark.fake_ephemeris
class TestFixedStarConjunctions:
    def test_fake_catalog_detects_conjunction(self) -> None:
        """Place the Sun on Regulus and confirm the conjunction is detected."""
        # 2025-06-01: Regulus ≈ 29°58' Leo ≈ 149.97° tropical.
        # For the fake, use a matching Sun longitude.
        fake = FakeEphemeris(
            longitudes={p: 0.0 for p in Planet.classical()} | {Planet.SUN: 149.97},
            star_longitudes={"Regulus": 149.97, "Aldebaran": 69.93},
            ascendant=10.0,
            midheaven=280.0,
        )
        data = ChartData(
            datetime=datetime(2025, 6, 1, 12, 0, tzinfo=UTC),
            place=Place(latitude=0.0, longitude=0.0),
        )
        chart = compute_natal_chart(data, ephemeris=fake)
        conj = compute_fixed_star_conjunctions(chart, orb=1.0, ephemeris=fake)
        stars = {c.star for c in conj}
        # Sun-Regulus should be detected.
        assert FixedStar.REGULUS in stars
        # Aldebaran at 69.93 is nowhere near any fake body (all at 0 or 149.97) → not detected.
        assert FixedStar.ALDEBARAN not in stars

    def test_orb_filter(self) -> None:
        """A star 5° from a body is not flagged with orb=1 but is with orb=10."""
        fake = FakeEphemeris(
            longitudes={p: 0.0 for p in Planet.classical()} | {Planet.SUN: 100.0},
            star_longitudes={"Regulus": 105.0},
        )
        data = ChartData(
            datetime=datetime(2025, 6, 1, 12, 0, tzinfo=UTC),
            place=Place(latitude=0.0, longitude=0.0),
        )
        chart = compute_natal_chart(data, ephemeris=fake)
        assert compute_fixed_star_conjunctions(chart, orb=1.0, ephemeris=fake) == ()
        wide = compute_fixed_star_conjunctions(chart, orb=10.0, ephemeris=fake)
        assert any(c.star is FixedStar.REGULUS for c in wide)
