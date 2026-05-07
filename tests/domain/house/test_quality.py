"""House quality classification (angular / succedent / cadent)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.pure


def test_angular_houses() -> None:
    from astrologica._internal.domain.house.quality import HouseQuality, house_quality

    for h in (1, 4, 7, 10):
        assert house_quality(h) is HouseQuality.ANGULAR


def test_succedent_houses() -> None:
    from astrologica._internal.domain.house.quality import HouseQuality, house_quality

    for h in (2, 5, 8, 11):
        assert house_quality(h) is HouseQuality.SUCCEDENT


def test_cadent_houses() -> None:
    from astrologica._internal.domain.house.quality import HouseQuality, house_quality

    for h in (3, 6, 9, 12):
        assert house_quality(h) is HouseQuality.CADENT


def test_house_quality_rejects_zero() -> None:
    from astrologica._internal.domain.house.quality import house_quality

    with pytest.raises(ValueError):
        house_quality(0)


def test_house_quality_rejects_thirteen() -> None:
    from astrologica._internal.domain.house.quality import house_quality

    with pytest.raises(ValueError):
        house_quality(13)
