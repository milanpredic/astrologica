"""astrologica.geo — optional geocoding + timezone helpers.

Requires the `[geo]` extra:

    pip install 'astrologica[geo]'

Exposes:

- `build_natal_chart(when, city, tradition=...)` — one-liner natal chart from
  a datetime-like value + city name.
- `build_horary_chart(when, city, question_house=...)` — horary chart cast
  at `when` from `city`, with significators + Moon VOC attached.
- `build_chart_data(local, place)` — naive datetime + `Place` → `ChartData`.
- `lookup_city(name)` — city name → `Place` (via `geonamescache`).
- `resolve_timezone(local, place)` — naive local datetime + `Place` → tz-aware.
- `timezone_name_for(place)` — `Place` → IANA timezone string.
- `elevation_of(place)` — `Place` → altitude in metres (needs `SRTM.py`).
"""

from astrologica.geo.chart import build_natal_chart
from astrologica.geo.chart_data import build_chart_data
from astrologica.geo.elevation import elevation_of
from astrologica.geo.horary import build_horary_chart
from astrologica.geo.place_lookup import lookup_city
from astrologica.geo.timezone import resolve_timezone, timezone_name_for

__all__ = [
    "build_chart_data",
    "build_horary_chart",
    "build_natal_chart",
    "elevation_of",
    "lookup_city",
    "resolve_timezone",
    "timezone_name_for",
]
