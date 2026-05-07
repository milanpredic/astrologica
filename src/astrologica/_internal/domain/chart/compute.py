"""compute_natal_chart — top-level orchestrator that produces a Chart from ChartData."""

from __future__ import annotations

from types import SimpleNamespace

from astrologica._internal.domain.almuten.compute import compute_almuten
from astrologica._internal.domain.almuten.figuris import compute_almuten_figuris
from astrologica._internal.domain.aspect.angle import Angle
from astrologica._internal.domain.aspect.compute import compute_aspects
from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.chart.chart_data import ChartData
from astrologica._internal.domain.chart.config import DEFAULT_CHART_CONFIG, ChartConfig
from astrologica._internal.domain.chart.tradition import ChartTradition
from astrologica._internal.domain.dignity.compute import compute_dignities
from astrologica._internal.domain.diurnal import compute_is_diurnal
from astrologica._internal.domain.house.compute import compute_house_cusps
from astrologica._internal.domain.house.placement import house_of
from astrologica._internal.domain.house.system import HouseSystem
from astrologica._internal.domain.lot.compute import compute_lots
from astrologica._internal.domain.orientality.compute import planet_orientality
from astrologica._internal.domain.planet.compute import compute_planet_positions
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition
from astrologica._internal.domain.solar_state.compute import planet_solar_state
from astrologica._internal.domain.syzygy.compute import compute_prenatal_syzygy
from astrologica._internal.ports.ephemeris import EphemerisPort

_OPT_IN_NODES: frozenset[Planet] = frozenset({Planet.TRUE_NODE, Planet.SOUTH_TRUE_NODE})


def compute_natal_chart(
    data: ChartData,
    house_system: HouseSystem,
    ephemeris: EphemerisPort,
    tradition: ChartTradition = ChartTradition.TRADITIONAL,
    *,
    include_nodes: bool = False,
    config: ChartConfig = DEFAULT_CHART_CONFIG,
) -> Chart:
    """Compute a natal chart for the given input bundle.

    `tradition` selects the body set:
    - `TRADITIONAL` (default): the 7 classical planets.
    - `MODERN`: classical + outer planets + lunar nodes.

    `include_nodes=True` adds Planet.TRUE_NODE and Planet.SOUTH_TRUE_NODE
    even under TRADITIONAL. Under MODERN this flag is a no-op (nodes are
    already included).

    `config` (ChartConfig) carries editorial knobs:
    - `terms_system` drives every dignity-aware computation in the chart
      (per-planet dignities, `term_ruler`, and almuten figuris).
    - `almuten` configures the eagerly-computed `chart.almuten_figuris`.
    """
    when = data.datetime
    ayanamsa = data.ayanamsa
    frame = data.frame
    terms_system = config.terms_system

    bodies: set[Planet] = set(tradition.bodies())
    if include_nodes:
        bodies |= _OPT_IN_NODES

    raw_planets = compute_planet_positions(
        when,
        ephemeris,
        bodies=frozenset(bodies),
        ayanamsa=ayanamsa,
        frame=frame,
        place=data.place,
    )
    house_cusps, ascendant, midheaven = compute_house_cusps(
        when, data.place, house_system, ephemeris, ayanamsa=ayanamsa
    )

    sun = raw_planets[Planet.SUN]
    is_diurnal = compute_is_diurnal(sun.longitude, float(ascendant))

    # First pass: positions + dignities + house placement (no Sun-relative state yet,
    # because solar_state and orientality need a fully-formed Sun position).
    bare_planets = {
        planet: PlanetPosition(
            planet=planet,
            position=pp.position,
            dignities=compute_dignities(
                planet, pp.longitude, is_diurnal=is_diurnal, terms_system=terms_system
            ),
            terms_system=terms_system,
            house=house_of(pp.longitude, house_cusps),
        )
        for planet, pp in raw_planets.items()
    }

    sun_pp = bare_planets[Planet.SUN]
    planets = {
        planet: PlanetPosition(
            planet=planet,
            position=pp.position,
            dignities=pp.dignities,
            terms_system=pp.terms_system,
            house=pp.house,
            solar_state=planet_solar_state(pp, sun_pp),
            orientality=planet_orientality(planet, bare_planets),
        )
        for planet, pp in bare_planets.items()
    }

    angle_anchors = SimpleNamespace(ascendant=float(ascendant), midheaven=float(midheaven))
    aspects = compute_aspects(
        planets,
        include_angles=(Angle.ASCENDANT, Angle.MIDHEAVEN),
        chart=angle_anchors,
    )
    lots = compute_lots(planets, float(ascendant), is_diurnal)
    syzygy = compute_prenatal_syzygy(when, ephemeris, ayanamsa=ayanamsa)

    chart_proto = SimpleNamespace(
        is_diurnal=is_diurnal,
        planets=planets,
        houses=house_cusps,
        ascendant=ascendant,
        lots={lot: lp for lot, lp in lots.items()},
        syzygy=syzygy,
    )
    almuten_figuris = compute_almuten_figuris(
        chart_proto,
        essential_weights=config.almuten.essential_weights,
        accidental_weights=config.almuten.accidental_weights,
        modifiers=config.almuten.modifiers,
        sect_aware=config.almuten.sect_aware,
        terms_system=terms_system,
    )

    return Chart(
        data=data,
        house_system=house_system,
        tradition=tradition,
        config=config,
        ascendant=ascendant,
        midheaven=midheaven,
        is_diurnal=is_diurnal,
        syzygy=syzygy,
        planets=planets,
        houses=house_cusps,
        aspects=aspects,
        lots=lots,
        almuten_figuris=almuten_figuris,
    )


__all__ = ["compute_almuten", "compute_natal_chart"]
