"""build_horary_chart — top-level one-liner: flexible datetime + city name → HoraryChart."""

from __future__ import annotations

from astrologica.chart import ChartTradition
from astrologica.chart_data import ChartData
from astrologica.geo._coerce import DatetimeInput, resolve_when_and_place
from astrologica.horary import HoraryChart, compute_horary_chart


def build_horary_chart(
    when: DatetimeInput,
    city: str,
    question_house: int = 1,
    tradition: ChartTradition = ChartTradition.TRADITIONAL,
) -> HoraryChart:
    """Cast a horary chart from a datetime-like value + a city name.

    `when` accepts several shapes (see `build_natal_chart` for the full list).
    `question_house` is the house whose cusp's ruler is the "quesited"
    significator — e.g., 1 for the querent themselves, 7 for a relationship
    question, 10 for career.  `tradition` defaults to `TRADITIONAL` — horary
    is a traditional technique — but `MODERN` is accepted (it adds outer
    planets + nodes to the underlying chart; significator logic uses
    classical rulerships regardless).

    Raises `ValueError` on unparseable datetime, `LookupError` if no city matches,
    `TypeError` for other input shapes.
    """
    parsed, place = resolve_when_and_place(when, city)
    data = ChartData(datetime=parsed, place=place)
    return compute_horary_chart(data, question_house=question_house, tradition=tradition)
