"""Chart — aggregate root, the output of compute_natal_chart."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from astrologica._internal.domain.almuten.types import AlmutenResult
from astrologica._internal.domain.aspect.aspect import Aspect
from astrologica._internal.domain.chart.chart_data import ChartData
from astrologica._internal.domain.chart.config import DEFAULT_CHART_CONFIG, ChartConfig
from astrologica._internal.domain.chart.tradition import ChartTradition
from astrologica._internal.domain.house.cusp import HouseCusp
from astrologica._internal.domain.house.system import HouseSystem
from astrologica._internal.domain.lot.lot import Lot
from astrologica._internal.domain.lot.position import LotPosition
from astrologica._internal.domain.measures.angle import Longitude
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition
from astrologica._internal.domain.syzygy.syzygy import Syzygy


@dataclass(frozen=True, slots=True)
class Chart:
    """A fully-computed natal chart. Immutable.

    Embeds the original `ChartData` so the source-of-truth stays traceable — given
    a `Chart`, you can always recover exactly what was asked for.
    """

    data: ChartData
    house_system: HouseSystem
    tradition: ChartTradition
    ascendant: Longitude
    midheaven: Longitude
    is_diurnal: bool
    syzygy: Syzygy
    planets: Mapping[Planet, PlanetPosition]
    houses: tuple[HouseCusp, ...]
    aspects: tuple[Aspect, ...]
    lots: Mapping[Lot, LotPosition]
    almuten_figuris: AlmutenResult
    config: ChartConfig = field(default=DEFAULT_CHART_CONFIG)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation of the chart."""
        return {
            "datetime": self.data.datetime.isoformat(),
            "utc": self.data.utc.isoformat(),
            "jd": self.data.jd,
            "place": {
                "latitude": self.data.place.latitude,
                "longitude": self.data.place.longitude,
            },
            "house_system": self.house_system.name,
            "tradition": self.tradition.name,
            "terms_system": self.config.terms_system.name,
            "ascendant": float(self.ascendant),
            "midheaven": float(self.midheaven),
            "is_diurnal": self.is_diurnal,
            "syzygy": {
                "kind": self.syzygy.kind.name,
                "when": self.syzygy.when.isoformat(),
                "longitude": float(self.syzygy.longitude),
                "sign": self.syzygy.sign.name,
            },
            "planets": {
                p.name: {
                    "longitude": pp.longitude,
                    "latitude": float(pp.position.latitude),
                    "speed": float(pp.position.speed),
                    "sign": pp.sign.name,
                    "degree_in_sign": pp.degree_in_sign,
                    "is_retrograde": pp.is_retrograde,
                    "house": pp.house,
                    "dignities": sorted(d.name for d in pp.dignities),
                    "face_ruler": pp.face_ruler.name,
                    "term_ruler": pp.term_ruler.name,
                    "triplicity_rulers": {
                        "day": pp.triplicity_rulers.day.name,
                        "night": pp.triplicity_rulers.night.name,
                        "participating": pp.triplicity_rulers.participating.name,
                    },
                    "monomoira_ruler": pp.monomoira_ruler.name,
                    "solar_state": pp.solar_state.name if pp.solar_state else None,
                    "orientality": pp.orientality.name if pp.orientality else None,
                }
                for p, pp in self.planets.items()
            },
            "houses": [
                {
                    "house": h.house.value,
                    "cusp": float(h.cusp),
                    "sign": h.sign.name,
                    "degree_in_sign": h.degree_in_sign,
                }
                for h in self.houses
            ],
            "aspects": [
                {
                    "first": a.first.name,
                    "second": a.second.name,
                    "kind": a.kind.name,
                    "orb": a.orb,
                    "applying": a.applying,
                    "exact": a.exact,
                }
                for a in self.aspects
            ],
            "lots": {
                lot.name: {
                    "longitude": float(lp.longitude),
                    "sign": lp.sign.name,
                    "degree_in_sign": lp.degree_in_sign,
                }
                for lot, lp in self.lots.items()
            },
            "almuten_figuris": {
                "winner": self.almuten_figuris.winner.name if self.almuten_figuris.winner else None,
                "totals": {p.name: t for p, t in self.almuten_figuris.totals.items()},
            },
        }
