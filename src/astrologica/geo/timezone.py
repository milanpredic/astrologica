"""Resolve a Place → IANA timezone and attach it to a naive local datetime.

Uses `timezonefinder` (offline, bundled data) to map lat/lon → IANA zone name,
then stdlib `zoneinfo` to build the tz-aware datetime.
"""

from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Any
from zoneinfo import ZoneInfo

from astrologica.place import Place


@lru_cache(maxsize=1)
def _tf() -> Any:
    try:
        from timezonefinder import TimezoneFinder
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "`resolve_timezone` / `timezone_name_for` require the `[geo]` extra: "
            "`uv add 'astrologica[geo]'` (or `pip install 'astrologica[geo]'`)"
        ) from e
    return TimezoneFinder()


def timezone_name_for(place: Place) -> str:
    """IANA timezone name (e.g. 'America/New_York') for a Place."""
    name: str | None = _tf().timezone_at(lat=place.latitude, lng=place.longitude)
    if name is None:
        raise LookupError(f"Could not determine timezone for {place!r}")
    return name


def resolve_timezone(local: datetime, place: Place) -> datetime:
    """Attach the IANA timezone of `place` to a naive local datetime.

    Raises `ValueError` if `local` is already tz-aware (callers who already have
    tz-aware datetimes don't need this helper).
    """
    if local.tzinfo is not None:
        raise ValueError("resolve_timezone expects a naive datetime; already has tzinfo")
    tz = ZoneInfo(timezone_name_for(place))
    return local.replace(tzinfo=tz)
