"""Horary chart — significators + moon VOC, real behaviour."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from astrologica.chart_data import ChartData
from astrologica.horary import compute_horary_chart
from astrologica.house import HouseSystem
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.swisseph import SwissEphemerisAdapter
from tests.fakes.fake_ephemeris import FakeEphemeris


@pytest.fixture
def question_data() -> ChartData:
    return ChartData(
        datetime=datetime(2025, 6, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=51.4779, longitude=-0.0015),
    )


@pytest.mark.infrastructure
class TestHoraryChartAgainstRealEphemeris:
    def test_default_house_system_is_regiomontanus(self, question_data) -> None:
        hc = compute_horary_chart(question_data, ephemeris=SwissEphemerisAdapter())
        assert hc.chart.house_system is HouseSystem.REGIOMONTANUS

    def test_significators_are_classical_planets(self, question_data) -> None:
        hc = compute_horary_chart(
            question_data, question_house=7, ephemeris=SwissEphemerisAdapter()
        )
        assert hc.significator_of_querent.is_classical
        assert hc.significator_of_quesited.is_classical

    def test_moon_voc_is_boolean(self, question_data) -> None:
        hc = compute_horary_chart(question_data, ephemeris=SwissEphemerisAdapter())
        assert isinstance(hc.moon_is_void_of_course, bool)

    def test_question_house_out_of_range_rejected(self, question_data) -> None:
        with pytest.raises(ValueError):
            compute_horary_chart(
                question_data, question_house=13, ephemeris=SwissEphemerisAdapter()
            )


@pytest.mark.fake_ephemeris
class TestSignificatorResolution:
    """Significators come from classical domicile rulership of the chart's
    ASC and question-house cusps, verified with deterministic fake data."""

    def _data(self) -> ChartData:
        return ChartData(
            datetime=datetime(2025, 6, 1, 12, 0, tzinfo=UTC),
            place=Place(latitude=40.0, longitude=-74.0),
        )

    def test_asc_in_aries_gives_mars_querent(self) -> None:
        """ASC at 10° Aries → Mars rules Aries → querent significator = Mars."""
        fake = FakeEphemeris(
            longitudes={p: 0.0 for p in Planet.classical()},
            speeds={p: 1.0 for p in Planet.classical()},
            ascendant=10.0,
            midheaven=280.0,
        )
        hc = compute_horary_chart(self._data(), ephemeris=fake)
        assert hc.significator_of_querent is Planet.MARS

    def test_asc_in_cancer_gives_moon_querent(self) -> None:
        """ASC at 100° (10° Cancer) → Moon rules Cancer."""
        fake = FakeEphemeris(
            longitudes={p: 0.0 for p in Planet.classical()},
            speeds={p: 1.0 for p in Planet.classical()},
            ascendant=100.0,
            midheaven=10.0,
        )
        hc = compute_horary_chart(self._data(), ephemeris=fake)
        assert hc.significator_of_querent is Planet.MOON

    def test_seventh_house_significator_is_opposite_ruler(self) -> None:
        """ASC at 10° Aries → 7th cusp in Libra → Venus rules Libra."""
        fake = FakeEphemeris(
            longitudes={p: 0.0 for p in Planet.classical()},
            speeds={p: 1.0 for p in Planet.classical()},
            ascendant=10.0,
            midheaven=280.0,
        )
        hc = compute_horary_chart(self._data(), ephemeris=fake, question_house=7)
        assert hc.significator_of_quesited is Planet.VENUS


@pytest.mark.fake_ephemeris
class TestMoonVOC:
    """Moon VOC = Moon forms no applying Ptolemaic aspect to a classical
    planet before leaving its current sign."""

    def _data(self) -> ChartData:
        return ChartData(
            datetime=datetime(2025, 6, 1, 12, 0, tzinfo=UTC),
            place=Place(latitude=40.0, longitude=-74.0),
        )

    def test_moon_with_applying_sextile_is_not_voc(self) -> None:
        """Moon at 5° Aries (moving 13°/day) with Saturn at 10° Gemini (70°).

        Separation = 65°. Aspect target is sextile (60°). Abs_sep > angle and
        Moon's forward motion shrinks the separation toward 60° → applying.
        The aspect completes in about (65−60)/13 ≈ 9 h, well within Moon's
        remaining 25° in Aries → not VOC.
        """
        fake = FakeEphemeris(
            longitudes={
                **{p: 0.0 for p in Planet.classical()},
                Planet.MOON: 5.0,
                Planet.SATURN: 70.0,
            },
            speeds={
                Planet.MOON: 13.0,
                Planet.SATURN: 0.03,
                Planet.SUN: 1.0,
                Planet.MERCURY: 1.2,
                Planet.VENUS: 1.1,
                Planet.MARS: 0.5,
                Planet.JUPITER: 0.08,
            },
            ascendant=10.0,
            midheaven=280.0,
        )
        hc = compute_horary_chart(self._data(), ephemeris=fake)
        assert hc.moon_is_void_of_course is False

    def test_moon_isolated_at_end_of_sign_is_voc(self) -> None:
        """Moon at 29° Aries with all other planets at 15° Aries (behind
        Moon). Moon is separating from all of them; no aspect applies
        within the 1° remaining in the sign → VOC."""
        fake = FakeEphemeris(
            longitudes={
                Planet.MOON: 29.0,
                Planet.SUN: 15.0,
                Planet.MERCURY: 15.0,
                Planet.VENUS: 15.0,
                Planet.MARS: 15.0,
                Planet.JUPITER: 15.0,
                Planet.SATURN: 15.0,
            },
            speeds={
                Planet.MOON: 13.0,
                Planet.SUN: 1.0,
                Planet.MERCURY: 1.2,
                Planet.VENUS: 1.1,
                Planet.MARS: 0.5,
                Planet.JUPITER: 0.08,
                Planet.SATURN: 0.03,
            },
            ascendant=10.0,
            midheaven=280.0,
        )
        hc = compute_horary_chart(self._data(), ephemeris=fake)
        assert hc.moon_is_void_of_course is True
