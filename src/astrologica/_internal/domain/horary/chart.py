"""HoraryChart — the natal-style chart cast for the moment a question is asked.

Extends the ordinary `Chart` with horary-specific metadata:
- `question_house`: which house the question's subject belongs to (1 for
  querent concerns, 7 for relationship, 10 for career, etc.).
- `significator_of_querent`: the planet ruling the ascendant.
- `significator_of_quesited`: the planet ruling the question's house.
- `moon_is_void_of_course`: whether the Moon has no applying Ptolemaic
  aspect before leaving its current sign — a classical horary caveat
  indicating "nothing will come of the matter".
"""

from __future__ import annotations

from dataclasses import dataclass

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.planet.planet import Planet


@dataclass(frozen=True, slots=True)
class HoraryChart:
    """A horary chart: base chart + question-specific significators."""

    chart: Chart
    question_house: int
    significator_of_querent: Planet
    significator_of_quesited: Planet
    moon_is_void_of_course: bool
