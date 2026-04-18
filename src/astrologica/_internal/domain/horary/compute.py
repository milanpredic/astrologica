"""compute_horary_chart — build a horary chart with significators + moon VOC.

Horary defaults:
- House system: **Regiomontanus** (the classical horary standard).
- Tradition: **TRADITIONAL** (the 7 classical planets) — horary is a
  traditional technique and uses classical rulerships; passing `MODERN`
  includes outer planets in the underlying chart but does not change
  significator resolution or Moon VOC (both use classical planets only).
- Significator of the querent: domicile ruler of the Ascendant.
- Significator of the quesited: domicile ruler of the `question_house` cusp.
- Moon VOC (void of course): the Moon forms no applying Ptolemaic aspect
  with any other planet before leaving its current sign.
"""

from __future__ import annotations

from astrologica._internal.domain.chart.chart_data import ChartData
from astrologica._internal.domain.chart.compute import compute_natal_chart
from astrologica._internal.domain.chart.tradition import ChartTradition
from astrologica._internal.domain.horary.chart import HoraryChart
from astrologica._internal.domain.house.system import HouseSystem
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign
from astrologica._internal.domain.tables.rulerships import DOMICILE
from astrologica._internal.ports.ephemeris import EphemerisPort

_PTOLEMAIC_ANGLES = (0.0, 60.0, 90.0, 120.0, 180.0)


def compute_horary_chart(
    data: ChartData,
    ephemeris: EphemerisPort,
    question_house: int = 1,
    tradition: ChartTradition = ChartTradition.TRADITIONAL,
) -> HoraryChart:
    """Compute a horary chart for a question asked at `data.datetime`.

    `question_house` is the house whose cusp's ruler is the "quesited"
    significator — e.g., 1 for the querent themself, 7 for a relationship
    question, 10 for career. `tradition` chooses the body set of the
    underlying chart (classical 7 vs classical + outers + nodes); significator
    resolution and Moon VOC detection always use classical planets regardless.
    """
    if not 1 <= question_house <= 12:
        raise ValueError("question_house must be in 1..12")

    chart = compute_natal_chart(
        data,
        HouseSystem.REGIOMONTANUS,
        ephemeris,
        tradition=tradition,
    )

    asc_sign = Sign.of(float(chart.ascendant))
    sig_querent = DOMICILE.get(asc_sign)
    if sig_querent is None:
        raise ValueError(f"no domicile ruler for ASC sign {asc_sign}")

    q_cusp = float(chart.houses[question_house - 1].cusp)
    q_sign = Sign.of(q_cusp)
    sig_quesited = DOMICILE.get(q_sign)
    if sig_quesited is None:
        raise ValueError(f"no domicile ruler for question-house sign {q_sign}")

    moon_voc = _moon_is_void_of_course(chart)

    return HoraryChart(
        chart=chart,
        question_house=question_house,
        significator_of_querent=sig_querent,
        significator_of_quesited=sig_quesited,
        moon_is_void_of_course=moon_voc,
    )


def _moon_is_void_of_course(chart) -> bool:  # type: ignore[no-untyped-def]
    """A Moon is VOC if it makes no applying Ptolemaic aspect before leaving
    its current sign."""
    from astrologica._internal.domain.aspect.aspect import Aspect

    moon_pos = chart.planets[Planet.MOON]
    moon_lon = float(moon_pos.longitude)
    moon_sign = Sign.of(moon_lon)
    degrees_to_sign_change = 30.0 - (moon_lon - moon_sign.value * 30.0)

    # Scan the existing aspect list for an applying aspect involving the Moon.
    applying_before_sign_change = False
    for a in chart.aspects:
        assert isinstance(a, Aspect)
        if Planet.MOON not in (a.first, a.second):
            continue
        if a.applying:
            # Does the Moon reach exact aspect before leaving its sign?
            # Approximate via orb and speed — Moon moves ~13°/day.
            # If a.orb < degrees_to_sign_change, the Moon catches the aspect
            # within its current sign.
            if a.orb < degrees_to_sign_change:
                applying_before_sign_change = True
                break

    return not applying_before_sign_change
