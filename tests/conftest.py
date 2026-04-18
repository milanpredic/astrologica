"""Shared pytest configuration — adds the tests/ directory to sys.path for fakes."""

from __future__ import annotations

import sys
from pathlib import Path

# Make `from tests.fakes.fake_ephemeris import FakeEphemeris` work.
_TESTS_ROOT = Path(__file__).parent.parent
if str(_TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_TESTS_ROOT))
