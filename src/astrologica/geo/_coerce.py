"""Shared input-coercion helpers for the geo builders.

Both `build_natal_chart` and `build_horary_chart` accept a flexible
datetime-like input plus a city name. This module normalises those inputs
into a tz-aware `datetime` and a `Place`.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Union

from astrologica.geo.place_lookup import lookup_city
from astrologica.geo.timezone import resolve_timezone
from astrologica.place import Place

DatetimeInput = Union[str, int, float, datetime]


def resolve_when_and_place(when: DatetimeInput, city: str) -> tuple[datetime, Place]:
    """Look up `city` to a `Place`, then coerce `when` to a tz-aware datetime.

    `when` accepts:
    - **ISO 8601 string**: ``"1990-05-15T14:30"`` (naive, resolved to city tz)
      or ``"1990-05-15T14:30:00-04:00"`` (tz-aware).
    - **Unix timestamp** (`int` / `float`): seconds since epoch, UTC.
    - **`datetime`**: tz-aware kept as-is; naive resolved to city tz.
    """
    place = lookup_city(city)
    parsed = _coerce_to_datetime(when, place)
    return parsed, place


def _coerce_to_datetime(when: DatetimeInput, place: Place) -> datetime:
    """Normalise any supported input shape to a tz-aware datetime."""
    if isinstance(when, datetime):
        parsed = when
    elif isinstance(when, bool):
        # bool is a subclass of int; reject explicitly to avoid nonsensical timestamps.
        raise TypeError("`when` cannot be a bool")
    elif isinstance(when, (int, float)):
        # Unix timestamp is an unambiguous UTC instant — no city-tz lookup needed.
        return datetime.fromtimestamp(when, tz=UTC)
    elif isinstance(when, str):
        parsed = datetime.fromisoformat(when)
    else:
        raise TypeError(f"`when` must be str, int, float, or datetime; got {type(when).__name__}")

    if parsed.tzinfo is None:
        parsed = resolve_timezone(parsed, place)
    return parsed
