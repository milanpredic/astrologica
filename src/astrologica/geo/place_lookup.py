"""Look up a Place by city name — thin wrapper over `geonamescache`."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from astrologica.place import Place


@lru_cache(maxsize=1)
def _cache() -> Any:
    try:
        import geonamescache
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "`lookup_city` requires the `[geo]` extra: "
            "`uv add 'astrologica[geo]'` (or `pip install 'astrologica[geo]'`)"
        ) from e
    return geonamescache.GeonamesCache()


def lookup_city(name: str) -> Place:
    """Resolve a city name to a `Place`. Raises `LookupError` if nothing matches.

    If multiple cities match (same name in different countries), the most populous
    one wins. Case-insensitive; searches canonical names and alternate names.
    """
    cities: dict[str, dict[str, Any]] = _cache().get_cities()
    needle = name.strip().casefold()

    best: dict[str, Any] | None = None
    for city in cities.values():
        candidates = [city["name"]] + list(city.get("alternatenames", []))
        if any(c.casefold() == needle for c in candidates):
            if best is None or city["population"] > best["population"]:
                best = city

    if best is None:
        raise LookupError(f"No city found for name {name!r}")

    return Place(latitude=best["latitude"], longitude=best["longitude"])
