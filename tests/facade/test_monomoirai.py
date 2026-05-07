"""Public-facade smoke test for astrologica.monomoirai."""

from __future__ import annotations

import pytest

from astrologica import Planet

pytestmark = pytest.mark.pure


def test_monomoirai_facade_exports() -> None:
    from astrologica.monomoirai import MONOMOIRAI, monomoira_of

    assert monomoira_of(0.0) is Planet.MARS
    assert MONOMOIRAI
