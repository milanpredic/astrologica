"""compute_natal_chart — top-level orchestrator that produces a Chart from ChartData."""

from __future__ import annotations

from astrologica._internal.domain.aspect.compute import compute_aspects
from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.chart.chart_data import ChartData
from astrologica._internal.domain.chart.tradition import ChartTradition
from astrologica._internal.domain.dignity.compute import compute_dignities
from astrologica._internal.domain.diurnal import compute_is_diurnal
from astrologica._internal.domain.house.compute import compute_house_cusps
from astrologica._internal.domain.house.system import HouseSystem
from astrologica._internal.domain.lot.compute import compute_lots
from astrologica._internal.domain.planet.compute import compute_planet_positions
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition
from astrologica._internal.domain.syzygy.compute import compute_prenatal_syzygy
from astrologica._internal.ports.ephemeris import EphemerisPort


def compute_natal_chart(
    data: ChartData,
    house_system: HouseSystem,
    ephemeris: EphemerisPort,
    tradition: ChartTradition = ChartTradition.TRADITIONAL,
) -> Chart:
    """Compute a natal chart for the given input bundle.

    `tradition` selects the body set:
    - `TRADITIONAL` (default): the 7 classical planets.
    - `MODERN`: classical + outer planets + lunar nodes.

    Domain-layer orchestrator: requires an explicit `EphemerisPort`. The public
    facade (`astrologica.chart.compute_natal_chart`) wraps this and constructs a
    default `SwissEphemerisAdapter` when the caller does not inject one.
    """
    when = data.datetime
    ayanamsa = data.ayanamsa
    frame = data.frame
    raw_planets = compute_planet_positions(
        when,
        ephemeris,
        bodies=tradition.bodies(),
        ayanamsa=ayanamsa,
        frame=frame,
        place=data.place,
    )
    house_cusps, ascendant, midheaven = compute_house_cusps(
        when, data.place, house_system, ephemeris, ayanamsa=ayanamsa
    )

    sun = raw_planets[Planet.SUN]
    is_diurnal = compute_is_diurnal(sun.longitude, float(ascendant))

    planets = {
        planet: PlanetPosition(
            planet=planet,
            position=pp.position,
            dignities=compute_dignities(planet, pp.longitude, is_diurnal=is_diurnal),
        )
        for planet, pp in raw_planets.items()
    }

    aspects = compute_aspects(planets)
    lots = compute_lots(planets, float(ascendant), is_diurnal)
    syzygy = compute_prenatal_syzygy(when, ephemeris, ayanamsa=ayanamsa)

    return Chart(
        data=data,
        house_system=house_system,
        tradition=tradition,
        ascendant=ascendant,
        midheaven=midheaven,
        is_diurnal=is_diurnal,
        syzygy=syzygy,
        planets=planets,
        houses=house_cusps,
        aspects=aspects,
        lots=lots,
    )
