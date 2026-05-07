"""Public-facade smoke tests for Phase B modules."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.pure


def test_term_distribution_facade_exports() -> None:
    from astrologica.term_distribution import TermPeriod, compute_term_distribution  # noqa: F401


def test_decennials_facade_exports() -> None:
    from astrologica.decennials import DecennialPeriod, compute_decennials  # noqa: F401


def test_profection_facade_exports() -> None:
    from astrologica.profection import ProfectionPeriod, compute_annual_profection  # noqa: F401


def test_returns_facade_includes_saturn_return() -> None:
    from astrologica.returns import compute_saturn_return  # noqa: F401


def test_top_level_phase_b_exports() -> None:
    import astrologica as a

    for name in (
        "DecennialPeriod",
        "ProfectionPeriod",
        "TermPeriod",
        "compute_annual_profection",
        "compute_decennials",
        "compute_saturn_return",
        "compute_term_distribution",
    ):
        assert hasattr(a, name), f"astrologica.{name} not re-exported"
