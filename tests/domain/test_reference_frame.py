"""ReferenceFrame enum — geo/topo/helio."""

from __future__ import annotations

import pytest

from astrologica._internal.domain.reference_frame import ReferenceFrame

pytestmark = pytest.mark.pure


class TestReferenceFrame:
    def test_has_three_members(self) -> None:
        assert len(list(ReferenceFrame)) == 3

    def test_members_named(self) -> None:
        names = {f.name for f in ReferenceFrame}
        assert names == {"GEOCENTRIC", "TOPOCENTRIC", "HELIOCENTRIC"}
