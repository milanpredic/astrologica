"""Per-degree (monomoira) ruler lookup."""

from __future__ import annotations

import pytest

from astrologica import Planet, Sign

pytestmark = pytest.mark.pure


def test_monomoirai_table_has_12_signs_each_with_30_entries() -> None:
    from astrologica._internal.domain.tables.monomoirai import MONOMOIRAI

    assert set(MONOMOIRAI.keys()) == set(Sign)
    for sign, row in MONOMOIRAI.items():
        assert len(row) == 30, f"{sign}: {len(row)}"


def test_monomoira_of_aries_zero_is_mars() -> None:
    from astrologica._internal.domain.tables.monomoirai import monomoira_of

    assert monomoira_of(0.0) is Planet.MARS


def test_monomoira_of_aries_one_degree_is_sun() -> None:
    from astrologica._internal.domain.tables.monomoirai import monomoira_of

    assert monomoira_of(1.0) is Planet.SUN


def test_monomoira_of_taurus_zero_is_venus() -> None:
    from astrologica._internal.domain.tables.monomoirai import monomoira_of

    assert monomoira_of(30.0) is Planet.VENUS


def test_monomoira_of_floor_lookup_within_degree() -> None:
    from astrologica._internal.domain.tables.monomoirai import monomoira_of

    assert monomoira_of(0.999) is Planet.MARS
    assert monomoira_of(1.0) is Planet.SUN


def test_monomoira_of_normalizes_longitude() -> None:
    from astrologica._internal.domain.tables.monomoirai import monomoira_of

    assert monomoira_of(360.0) is monomoira_of(0.0)
    assert monomoira_of(-30.0) is monomoira_of(330.0)


def test_monomoira_of_aquarius_zero_is_saturn() -> None:
    from astrologica._internal.domain.tables.monomoirai import monomoira_of

    assert monomoira_of(300.0) is Planet.SATURN


def test_monomoira_of_covers_all_360_degrees_no_gaps() -> None:
    from astrologica._internal.domain.tables.monomoirai import monomoira_of

    classical = {
        Planet.SUN,
        Planet.MOON,
        Planet.MERCURY,
        Planet.VENUS,
        Planet.MARS,
        Planet.JUPITER,
        Planet.SATURN,
    }
    for d in range(360):
        ruler = monomoira_of(float(d))
        assert ruler in classical
