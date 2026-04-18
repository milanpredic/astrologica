"""compute_secondary_progressions — day-for-a-year progressed chart.

The secondary progression for age N years is the chart cast for the moment
(natal + N days), using the same birth place. This implements the oldest
and most widely used progression technique in Western astrology.

The progressed chart is returned as a full `Chart` using the natal's
tradition / ayanamsa / frame, evaluated at the progressed moment.
"""

from __future__ import annotations

from datetime import timedelta

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.chart.chart_data import ChartData
from astrologica._internal.domain.chart.compute import compute_natal_chart
from astrologica._internal.ports.ephemeris import EphemerisPort


def compute_secondary_progressions(
    natal: Chart,
    age_years: float,
    ephemeris: EphemerisPort,
) -> Chart:
    """Progressed chart for age `age_years` past the natal moment.

    One day equals one year (the traditional "day-for-a-year" key). For
    fractional years, the offset is `age_years * 1 day`, so a 30-year
    progression steps 30 days forward.
    """
    if age_years < 0:
        raise ValueError("age_years must be non-negative for secondary progressions")

    progressed_when = natal.data.datetime + timedelta(days=age_years)

    progressed_data = ChartData(
        datetime=progressed_when,
        place=natal.data.place,
        ayanamsa=natal.data.ayanamsa,
        frame=natal.data.frame,
    )
    return compute_natal_chart(
        progressed_data,
        natal.house_system,
        ephemeris,
        tradition=natal.tradition,
    )
