"""build_chart_data — one-line convenience: naive datetime + Place → ChartData.

Handy when you have raw local date/time + coordinates but don't know the IANA
timezone. Uses `resolve_timezone` under the hood to attach the correct `ZoneInfo`.
"""

from __future__ import annotations

from datetime import datetime

from astrologica.chart_data import ChartData
from astrologica.geo.timezone import resolve_timezone
from astrologica.place import Place


def build_chart_data(local: datetime, place: Place) -> ChartData:
    """Build a `ChartData` from a naive local datetime + Place.

    Resolves the IANA timezone for `place.latitude, place.longitude` via
    `timezonefinder`, attaches it to `local`, and returns a `ChartData`.
    """
    tz_aware = resolve_timezone(local, place)
    return ChartData(datetime=tz_aware, place=place)
