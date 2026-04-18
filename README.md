# astrologica

[![PyPI version](https://img.shields.io/pypi/v/astrologica.svg)](https://pypi.org/project/astrologica/)
[![Python versions](https://img.shields.io/pypi/pyversions/astrologica.svg)](https://pypi.org/project/astrologica/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

A Python astrology library.
Traditional Hellenistic focus, Swiss Ephemeris backed, domain-pure core.

## Install

```bash
pip install astrologica              # core
pip install 'astrologica[geo]'       # + city lookup, timezone, elevation helpers
```

## Quickstart

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from astrologica import ChartData, Place, Planet, compute_natal_chart

data = ChartData(
    datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("America/New_York")),
    place=Place(latitude=40.7128, longitude=-74.0060),
)

chart = compute_natal_chart(data)

print(chart.planets[Planet.SUN].sign)           # Sign.TAURUS
print(chart.planets[Planet.SUN].degree_in_sign) # 24.72
print(chart.planets[Planet.SUN].is_retrograde)  # False
print(chart.is_diurnal)                         # True
```

### Don't know the timezone? Use the `[geo]` extra.

```python
from astrologica import ChartTradition, Planet
from astrologica.geo import build_horary_chart, build_natal_chart

natal = build_natal_chart("1990-05-15T14:30", "New York")
modern = build_natal_chart("1990-05-15T14:30", "New York",
                           tradition=ChartTradition.MODERN)

horary = build_horary_chart("2025-06-01T12:00", "London", question_house=7)
print(horary.significator_of_querent, horary.significator_of_quesited)
print("Moon VOC:", horary.moon_is_void_of_course)
```

## What's in the box

Every feature is a top-level import from `astrologica`. The natal `Chart`
already contains planet positions, houses, aspects, lots, and the prenatal
syzygy — the cookbook below shows everything else you can layer on.

### Aspects

Computed automatically inside every `Chart`. To recompute standalone:

```python
from astrologica import compute_aspects
aspects = compute_aspects(chart.planets)
for a in aspects:
    print(a.first, a.kind, a.second, f"orb={a.orb:.2f}°",
          "applying" if a.applying else "separating")
```

### Transits — snapshot and range search

```python
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from astrologica import AspectKind, Planet, compute_transits, find_transits

now = datetime.now(ZoneInfo("UTC"))
snapshot = compute_transits(chart, now)
for ta in snapshot:
    print(f"t.{ta.transiting.name} {ta.kind.name} n.{ta.natal.name} orb={ta.orb:.2f}")

events = find_transits(
    chart,
    start=now,
    end=now + timedelta(days=365),
    transiting_bodies=[Planet.SATURN, Planet.JUPITER],
    natal_bodies=[Planet.SUN, Planet.MOON],
    aspects=[AspectKind.CONJUNCTION, AspectKind.OPPOSITION],
)
```

### Returns (solar / lunar)

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from astrologica import compute_lunar_return, compute_solar_return

sr = compute_solar_return(chart, year=2026)              # birthday chart
lr = compute_lunar_return(chart, after=datetime.now(ZoneInfo("UTC")))
```

Pass `place=Place(...)` to either for a **relocated** return.

### Secondary progressions

```python
from astrologica import compute_secondary_progressions
progressed = compute_secondary_progressions(chart, age_years=35.5)
```

### Primary directions (Placidian / Ptolemaic)

```python
from astrologica import (
    ArcKey, DirectionApproach, DirectionType,
    compute_primary_directions,
)

directions = compute_primary_directions(
    chart,
    key=ArcKey.NAIBOD,                     # arc-to-years conversion
    direction=DirectionType.DIRECT,        # or CONVERSE
    approach=DirectionApproach.ZODIACAL,   # or MUNDANE
)
for d in directions:
    print(f"{d.promissor.name} → {d.significator.name} {d.kind.name} "
          f"in {d.years:+.2f} years")
```

### Zodiacal releasing

```python
from astrologica import Lot, compute_zodiacal_releasing

periods = compute_zodiacal_releasing(
    chart,
    lot=Lot.SPIRIT,         # or Lot.FORTUNE
    max_level=4,            # 1 = major, 4 = sub-sub-sub
    year_length_days=360.0, # Valens' Egyptian year
)
for p in periods:
    marker = " LB" if p.is_lb else (" *peak*" if p.is_peak else "")
    print(f"L{p.level} {p.sign.name} {p.start.date()} → {p.end.date()}{marker}")
```

### Essential dignities

```python
from astrologica import TermsSystem, compute_dignities

sun = chart.planets[Planet.SUN]
print(sun.dignities)   # set on every PlanetPosition

# Or compute standalone at any longitude:
d = compute_dignities(
    Planet.JUPITER, longitude=5.0,
    is_diurnal=True,
    terms_system=TermsSystem.EGYPTIAN,  # or PTOLEMAIC / CHALDEAN / …
)
```

### Lots (Hellenistic) — classical seven + custom DSL

```python
from astrologica import Lot
print(chart.lots[Lot.FORTUNE].sign, chart.lots[Lot.FORTUNE].degree_in_sign)
```

Build your own parts:

```python
from astrologica import (
    CustomLot, LotFormula, Planet,
    CardinalAngle, CardinalAngleName, HouseCuspRef,
    LordOf, LordKind, RulerOf, RulerOfKind, PriorLot, SyzygyPoint,
    compute_custom_lot,
)

# Lot of Fortune, rebuilt:
fortune = CustomLot(
    name="Fortune",
    day=LotFormula(plus=(Planet.MOON,), minus=(Planet.SUN,)),
    night=LotFormula(plus=(Planet.SUN,), minus=(Planet.MOON,)),
)
# ASC is implicit in every formula; sect inversion is automatic.
longitude = compute_custom_lot(chart, fortune)
```

Formulas accept any `LotComponent`: bare `Planet`, `CardinalAngle` (e.g. MC),
`HouseCuspRef`, `LordOf` (house lord), `RulerOf` (sign ruler of a body),
`PriorLot`, or `SyzygyPoint`.

### Fixed stars (30 classical)

```python
from astrologica import FixedStar, compute_fixed_star_conjunctions

for conj in compute_fixed_star_conjunctions(chart, orb=1.0):
    print(f"{conj.body.name} conj {conj.star.name} (orb {conj.orb:.2f}°)")
```

### Midpoints

```python
from astrologica import compute_midpoints
mps = compute_midpoints(chart)  # 21 classical planet-pair midpoints
```

### Antiscia / contraantiscia

```python
from astrologica import compute_antiscion, compute_contraantiscion
compute_antiscion(15.0)         # solstitial-axis reflection
compute_contraantiscion(15.0)   # equinoctial-axis reflection
```

### Dodecatemorion (twelfth-part)

```python
from astrologica import DodecatemorionVariant, compute_dodecatemorion
compute_dodecatemorion(24.72)                                # Valens (default)
compute_dodecatemorion(24.72, DodecatemorionVariant.FIRMICUS)
```

### Planetary hours (Chaldean order)

```python
from datetime import date
from astrologica import Place, compute_planetary_hours

hours = compute_planetary_hours(
    on=date(2025, 6, 1),
    place=Place(latitude=51.5074, longitude=-0.1278),
)
for h in hours:
    print(h.ruler.name, h.start, "→", h.end, "day" if h.is_daytime else "night")
```

### Rise / set / MC / IC

```python
from datetime import date
from astrologica import Planet, Place, compute_rise_set

times = compute_rise_set(Planet.SUN, date(2025, 6, 1),
                         Place(latitude=51.5074, longitude=-0.1278))
print(times.rise, times.mc, times.set, times.ic)  # any may be None
```

### Sign rising times at a latitude

```python
from astrologica import Sign, compute_rising_times

rt = compute_rising_times(latitude_deg=40.7128)
for sign in Sign:
    print(sign.name, f"{rt[sign]:6.2f}°")  # sums to 360°
```

### Prenatal syzygy

Already attached to every chart — no extra call needed:

```python
print(chart.syzygy.kind.name, chart.syzygy.when, chart.syzygy.sign.name)
# → "NEW_MOON" or "FULL_MOON", the datetime, and the sign
```

Also callable directly against any moment if you need it standalone:

```python
from astrologica import SwissEphemerisAdapter, compute_prenatal_syzygy
s = compute_prenatal_syzygy(chart.data.datetime, SwissEphemerisAdapter())
```

### `find_time` — solve for a longitude crossing

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from astrologica import Planet, find_time

t = find_time(
    body=Planet.MARS,
    target_longitude=0.0,            # ingress into Aries
    start=datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC")),
    end=datetime(2027, 1, 1, tzinfo=ZoneInfo("UTC")),
)
```

### Horary

```python
from astrologica import ChartData, Place, compute_horary_chart
data = ChartData.from_iso("2025-06-01T14:30:00+01:00",
                          Place(latitude=51.5074, longitude=-0.1278))
hc = compute_horary_chart(data, question_house=7)
print(hc.significator_of_querent, hc.significator_of_quesited,
      "VOC" if hc.moon_is_void_of_course else "")
```

## Configuration

Every computation respects the `ChartData` and optional house system.

### House systems

```python
from astrologica import HouseSystem, compute_natal_chart
chart = compute_natal_chart(data, house_system=HouseSystem.PLACIDUS)
# Available: WHOLE_SIGN (default), PORPHYRY, ALCABITUS, REGIOMONTANUS, PLACIDUS
```

### Sidereal zodiac (21 ayanamsas)

```python
from astrologica import Ayanamsa, ChartData
data_sidereal = ChartData(datetime=..., place=..., ayanamsa=Ayanamsa.LAHIRI)
```

Available: `FAGAN_BRADLEY`, `LAHIRI`, `DELUCE`, `RAMAN`, `USHASHASHI`,
`KRISHNAMURTI`, `DJWHAL_KHUL`, `YUKTESHWAR`, `JN_BHASIN`, `BABYL_KUGLER1/2/3`,
`BABYL_HUBER`, `BABYL_ETPSC`, `ALDEBARAN_15TAU`, `HIPPARCHOS`, `SASSANIAN`,
`GALCENT_0SAG`, `J2000`, `J1900`, `B1950`.

### Reference frame

```python
from astrologica import ChartData, ReferenceFrame
data_topo = ChartData(datetime=..., place=..., frame=ReferenceFrame.TOPOCENTRIC)
# Frames: GEOCENTRIC (default), TOPOCENTRIC, HELIOCENTRIC
```

### Tradition (body set)

```python
from astrologica import ChartTradition
compute_natal_chart(data, tradition=ChartTradition.MODERN)
# TRADITIONAL: 7 classical. MODERN: + Uranus, Neptune, Pluto + lunar nodes.
```

### Terms systems

Supplied to `compute_dignities(...)`: `EGYPTIAN` (default),
`PTOLEMAIC`, `CHALDEAN`, `DOROTHEAN`, `ASTROLOGICAL_ASSOCIATION`.

### Ephemeris data

No download required. The Swiss adapter uses the built-in **Moshier**
analytical ephemeris for planet positions (accurate to a few arcseconds
from 3000 BC to 3000 AD), and ships a minimal `sefstars.txt` inside the
wheel so fixed-star lookups work out of the box.

If you want the higher-precision `.se1` planet data, download the files
from https://www.astro.com/ftp/swisseph/ephe/ (typically `sepl_18.se1` +
`semo_18.se1` covers 1800–2399 AD) and point the adapter at them:

```python
from astrologica import SwissEphemerisAdapter, compute_natal_chart
adapter = SwissEphemerisAdapter(ephe_path="/path/to/sweph/ephe")
chart = compute_natal_chart(data, ephemeris=adapter)
```

The same `adapter` can be reused across every `compute_*` call.

## Serialization

```python
import json
json.dumps(chart.to_dict(), indent=2)
# {
#   "datetime": "1990-05-15T14:30:00-04:00",
#   "utc": "1990-05-15T18:30:00+00:00",
#   "jd": 2448027.270833,
#   "place": {"latitude": 40.7128, "longitude": -74.006},
#   "house_system": "WHOLE_SIGN",
#   "tradition": "TRADITIONAL",
#   "ascendant": 171.12,
#   "midheaven": 81.04,
#   "is_diurnal": true,
#   "syzygy": {"kind": "FULL_MOON", ...},
#   "planets": {"SUN": {"sign": "TAURUS", "degree_in_sign": 24.72, ...}, ...},
#   "houses": [...], "aspects": [...], "lots": {...}
# }
```

## The `Chart` aggregate

| Field | Type | What it is |
|---|---|---|
| `data` | `ChartData` | the originating input (datetime, place, ayanamsa, frame) |
| `house_system` | `HouseSystem` | the system used for cusps |
| `tradition` | `ChartTradition` | `TRADITIONAL` or `MODERN` body set |
| `ascendant`, `midheaven` | `Longitude` | angles |
| `is_diurnal` | `bool` | sect — Sun above horizon? |
| `syzygy` | `Syzygy` | prenatal lunation (kind / when / longitude / sign) |
| `planets` | `Mapping[Planet, PlanetPosition]` | body positions + speed + dignities + retrograde |
| `houses` | `tuple[HouseCusp, ...]` | cusp longitudes |
| `aspects` | `tuple[Aspect, ...]` | Ptolemaic + semisextile + quincunx |
| `lots` | `Mapping[Lot, LotPosition]` | classical seven lots |

## Architecture

Port-adapter / hexagonal. The domain layer is `pyswisseph`-free; Swiss
Ephemeris lives behind an `EphemerisPort`. Public API at `astrologica.*`;
internals under `astrologica._internal.*` (enforced by import-linter
contracts). Frozen, slots-using dataclasses throughout; every chart is
JSON-serialisable via `Chart.to_dict()`. Type-hint friendly — the package
ships a `py.typed` marker.

Custom backends (e.g. for tests) are a drop-in:

```python
from astrologica import EphemerisPort, compute_natal_chart
class MyEphemeris(EphemerisPort): ...
compute_natal_chart(data, ephemeris=MyEphemeris())
```

## License

MIT — see [LICENSE](./LICENSE).
