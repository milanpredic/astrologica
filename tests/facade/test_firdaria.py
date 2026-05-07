"""Public-facade smoke test for astrologica.firdaria."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.pure


def test_firdaria_facade_exports() -> None:
    from astrologica.firdaria import (  # noqa: F401
        FirdariaPeriod,
        FirdariaSubPeriod,
        FirdariaTradition,
        compute_firdaria,
    )
