"""build_natal_chart — top-level one-liner: flexible datetime + city name → Chart."""

from __future__ import annotations

from astrologica.chart import Chart, ChartTradition, compute_natal_chart
from astrologica.chart_data import ChartData
from astrologica.geo._coerce import DatetimeInput, resolve_when_and_place
from astrologica.house import HouseSystem


def build_natal_chart(
    when: DatetimeInput,
    city: str,
    house_system: HouseSystem = HouseSystem.WHOLE_SIGN,
    tradition: ChartTradition = ChartTradition.TRADITIONAL,
) -> Chart:
    """Compute a natal chart from a datetime-like value + a city name.

    `when` accepts several shapes:

    - **ISO 8601 string**: e.g. ``"1990-05-15T14:30"`` (naive) or
      ``"1990-05-15T14:30:00-04:00"`` (tz-aware).
    - **Unix timestamp** (``int`` / ``float``): seconds since the epoch,
      always interpreted as UTC.
    - **`datetime` object**: tz-aware values are kept as-is; naive values are
      resolved against the city's IANA zone.

    If `when` is naive, the city's IANA timezone is auto-resolved from its
    lat/lon. `tradition` selects the body set (`TRADITIONAL` — classical 7,
    `MODERN` — + Uranus/Neptune/Pluto + lunar nodes). Default is TRADITIONAL.

    Raises `ValueError` on unparseable datetime, `LookupError` if no city matches,
    `TypeError` for other input shapes.
    """
    parsed, place = resolve_when_and_place(when, city)
    data = ChartData(datetime=parsed, place=place)
    return compute_natal_chart(data, house_system=house_system, tradition=tradition)
