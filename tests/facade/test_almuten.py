"""Public-facade smoke test for astrologica.almuten."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.pure


def test_almuten_facade_exports() -> None:
    from astrologica.almuten import (  # noqa: F401
        DEFAULT_ACCIDENTAL_WEIGHTS,
        DEFAULT_ALMUTEN_MODIFIERS,
        AlmutenModifiers,
        AlmutenPoint,
        AlmutenPointBreakdown,
        AlmutenResult,
        compute_almuten,
        compute_almuten_figuris,
    )
