"""Lat/lon → altitude in metres via SRTM (optional `[geo]` extra)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from astrologica.place import Place


@lru_cache(maxsize=1)
def _data() -> Any:
    try:
        import srtm
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "`elevation_of` requires the `[geo]` extra: "
            "`uv add 'astrologica[geo]'` (or `pip install 'astrologica[geo]'`)"
        ) from e
    return srtm.get_data()


def elevation_of(place: Place) -> float:
    """Return the ground elevation at `place` in metres, or 0.0 if SRTM has no tile."""
    result = _data().get_elevation(place.latitude, place.longitude)
    return float(result) if result is not None else 0.0
