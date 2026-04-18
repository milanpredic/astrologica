"""Public facade for horary astrology.

Cast a chart for the moment a question was asked, wrapped with horary-specific
significators:

```python
hc = compute_horary_chart(chart_data, question_house=7)  # relationship question
print(hc.significator_of_querent, hc.significator_of_quesited)
if hc.moon_is_void_of_course:
    print("Moon is VOC — traditional: no action will come of this question.")
```
"""

from __future__ import annotations

from astrologica._internal.domain.chart.chart_data import ChartData
from astrologica._internal.domain.chart.tradition import ChartTradition
from astrologica._internal.domain.horary import HoraryChart
from astrologica._internal.domain.horary.compute import (
    compute_horary_chart as _compute_horary_chart,
)
from astrologica._internal.infrastructure.ephemeris.swiss import SwissEphemerisAdapter
from astrologica._internal.ports.ephemeris import EphemerisPort

__all__ = ["HoraryChart", "compute_horary_chart"]


def compute_horary_chart(
    data: ChartData,
    question_house: int = 1,
    ephemeris: EphemerisPort | None = None,
    tradition: ChartTradition = ChartTradition.TRADITIONAL,
) -> HoraryChart:
    """Cast a horary chart for the moment in `data` with significators attached."""
    adapter = ephemeris if ephemeris is not None else SwissEphemerisAdapter()
    return _compute_horary_chart(data, adapter, question_house=question_house, tradition=tradition)
