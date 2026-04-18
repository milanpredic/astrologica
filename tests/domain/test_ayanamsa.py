"""Ayanamsa enum — the 21 sidereal modes supported by Swiss Ephemeris."""

from __future__ import annotations

import pytest

from astrologica._internal.domain.ayanamsa import Ayanamsa

pytestmark = pytest.mark.pure


class TestAyanamsa:
    def test_has_twenty_one_members(self) -> None:
        assert len(list(Ayanamsa)) == 21

    def test_contains_the_major_modes(self) -> None:
        names = {a.name for a in Ayanamsa}
        for required in (
            "FAGAN_BRADLEY",
            "LAHIRI",
            "DELUCE",
            "RAMAN",
            "USHASHASHI",
            "KRISHNAMURTI",
            "DJWHAL_KHUL",
            "YUKTESHWAR",
            "JN_BHASIN",
            "BABYL_KUGLER1",
            "BABYL_KUGLER2",
            "BABYL_KUGLER3",
            "BABYL_HUBER",
            "BABYL_ETPSC",
            "ALDEBARAN_15TAU",
            "HIPPARCHOS",
            "SASSANIAN",
            "GALCENT_0SAG",
            "J2000",
            "J1900",
            "B1950",
        ):
            assert required in names
