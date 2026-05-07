"""Public-facade smoke test for astrologica.orientality."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.pure


def test_orientality_facade_exports() -> None:
    from astrologica.orientality import Orientality, planet_orientality  # noqa: F401
