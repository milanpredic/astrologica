"""compute_transits — snapshot transit-to-natal aspects."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from astrologica.aspect import AspectKind
from astrologica.chart import compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.place import Place
from astrologica.planet import Planet
from astrologica.transits import compute_transits
from tests.fakes.fake_ephemeris import FakeEphemeris

pytestmark = pytest.mark.fake_ephemeris


@pytest.fixture
def natal_fake() -> FakeEphemeris:
    return FakeEphemeris(
        longitudes={
            Planet.SUN: 50.0,  # 20° Taurus
            Planet.MOON: 100.0,
            Planet.MERCURY: 40.0,
            Planet.VENUS: 70.0,
            Planet.MARS: 200.0,
            Planet.JUPITER: 300.0,
            Planet.SATURN: 250.0,
        },
        speeds={
            Planet.SUN: 1.0,
            Planet.MOON: 13.0,
            Planet.MERCURY: 1.2,
            Planet.VENUS: 1.1,
            Planet.MARS: 0.5,
            Planet.JUPITER: 0.08,
            Planet.SATURN: 0.03,
        },
        ascendant=10.0,
        midheaven=280.0,
        last_lunation_jd=2451545.0,
        last_lunation_moon_lon=50.0,
    )


@pytest.fixture
def natal_data() -> ChartData:
    return ChartData(
        datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        place=Place(latitude=40.0, longitude=-74.0),
    )


class TestComputeTransits:
    def test_returns_transit_aspect_shape(self, natal_data, natal_fake) -> None:
        natal = compute_natal_chart(natal_data, ephemeris=natal_fake)
        result = compute_transits(
            natal, datetime(2000, 1, 1, 12, 0, tzinfo=UTC), ephemeris=natal_fake
        )
        assert all(hasattr(a, "transiting") and hasattr(a, "natal") for a in result)

    def test_transit_to_self_is_exact_conjunction_on_birth_moment(
        self, natal_data, natal_fake
    ) -> None:
        """Transiting positions = natal positions at birth → exact self-conjunctions."""
        natal = compute_natal_chart(natal_data, ephemeris=natal_fake)
        result = compute_transits(natal, natal_data.datetime, ephemeris=natal_fake)
        exact_self_conjunctions = [
            a
            for a in result
            if a.kind is AspectKind.CONJUNCTION and a.transiting is a.natal and a.exact
        ]
        # The 7 classical bodies each form an exact self-conjunction.
        assert len(exact_self_conjunctions) == 7

    def test_transit_sun_trines_natal_saturn(self, natal_data) -> None:
        """Natal Saturn at 250°; transit Sun placed at 250 − 120 = 130° → exact trine."""
        natal_eph = FakeEphemeris(
            longitudes={
                Planet.SUN: 50.0,
                Planet.MOON: 0.0,
                Planet.MERCURY: 0.0,
                Planet.VENUS: 0.0,
                Planet.MARS: 0.0,
                Planet.JUPITER: 0.0,
                Planet.SATURN: 250.0,
            },
            speeds={p: 1.0 for p in Planet.classical()},
            last_lunation_jd=2451545.0,
            last_lunation_moon_lon=50.0,
        )
        transit_eph = FakeEphemeris(
            longitudes={p: 0.0 for p in Planet.classical()} | {Planet.SUN: 130.0},
            speeds={p: 1.0 for p in Planet.classical()},
            last_lunation_jd=2451545.0,
            last_lunation_moon_lon=130.0,
        )
        natal = compute_natal_chart(natal_data, ephemeris=natal_eph)
        future = datetime(2001, 1, 1, 12, 0, tzinfo=UTC)
        result = compute_transits(natal, future, ephemeris=transit_eph)

        sun_saturn = [a for a in result if a.transiting is Planet.SUN and a.natal is Planet.SATURN]
        assert len(sun_saturn) == 1
        assert sun_saturn[0].kind is AspectKind.TRINE
        assert sun_saturn[0].exact is True

    def test_deterministic_ordering(self, natal_data, natal_fake) -> None:
        natal = compute_natal_chart(natal_data, ephemeris=natal_fake)
        later = natal_data.datetime + timedelta(days=1)
        a = compute_transits(natal, later, ephemeris=natal_fake)
        b = compute_transits(natal, later, ephemeris=natal_fake)
        assert a == b
