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

sun = chart.planets[Planet.SUN]
print(sun.sign)                # Sign.TAURUS
print(sun.degree_in_sign)      # 24.72
print(sun.is_retrograde)       # False
print(sun.dignities)           # frozenset() — Sun has no essential dignity here
print(sun.house)               # 9
print(sun.solar_state)         # SolarState.FREE
print(sun.orientality)         # Orientality.NEUTRAL (Sun & Moon are NEUTRAL)
print(sun.face_ruler)          # Planet.SATURN  (third decan of Taurus)
print(sun.term_ruler)          # Planet.SATURN  (Egyptian: 27–30° Taurus)
print(sun.triplicity_rulers)   # TriplicityRulers(day=VENUS, night=MOON, participating=MARS)
print(sun.monomoira_ruler)     # Planet.SATURN  (per-degree ruler at 25° Taurus)
print(chart.is_diurnal)        # True
print(chart.almuten_figuris.winner)  # Planet.VENUS — chart's overall ruler
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

**Time-lord techniques.** Five complementary systems for activating the
chart over time: `compute_zodiacal_releasing` (Valens, releasing from
Spirit or Fortune), `compute_firdaria` (Persian fixed-period, two nocturnal
traditions), `compute_decennials` (Valens decennia, 10y9m per planet),
`compute_term_distribution` (Naibod-directed Ascendant through term
boundaries), and `compute_annual_profection` (Ptolemaic 12-house cycle).
Pair any of them with `compute_almuten_figuris` for the chart's overall
ruler, or `compute_saturn_return` and `compute_secondary_progressions`
for life-stage markers.

**Planetary conditions.** `compute_sect_status` (in-sect / halb / hayz),
`chart_besiegement` (bodily and by-rays malefic enclosure),
`chart_void_of_course` (perfection-before-sign-exit criterion),
`compute_moon_phase` (quarters), `in_via_combusta`, plus solar states
(cazimi / combust / under beams) and orientality on every position.

### Aspects

Computed automatically inside every `Chart`. To recompute standalone:

```python
from astrologica import compute_aspects
aspects = compute_aspects(chart.planets)
for a in aspects:
    print(a.first, a.kind, a.second, f"orb={a.orb:.2f}°",
          "applying" if a.applying else "separating")
```

Orb policies are pluggable. Besides the per-aspect-kind default, the classical
**Lilly moiety** policy is built in — the orb belongs to the *planets* (sum of
the two bodies' half-orbs, aspect-kind-independent; CA I p.107/p.127):

```python
from astrologica import LILLY_ORBS, compute_aspects, lilly_moiety_orb

aspects = compute_aspects(chart.planets, orb_policy=lilly_moiety_orb)
# LILLY_ORBS: Saturn 10°, Jupiter 12°, Mars 7.5°, Sun 15°, Venus 8°,
# Mercury 7°, Moon 12.5° — e.g. a Venus–Saturn trine admits (8+10)/2 = 9°.
```

### Sect — in-sect, halb, hayz

Per-planet sect conditions: sect membership (Mercury by orientality), the
ecliptic above/below-horizon placement, **halb** (correct sect + hemisphere)
and **hayz** (halb + planet/sign gender agreement):

```python
from astrologica import Planet, compute_sect_status

status = compute_sect_status(chart)[Planet.MERCURY]
print(status.planet_sect, status.in_sect, status.in_halb, status.in_hayz)
```

### Traditional conditions — via combusta, moon phase, besiegement, void of course

```python
from astrologica import (
    Planet,
    chart_besiegement,
    chart_void_of_course,
    compute_moon_phase,
    in_via_combusta,
)

in_via_combusta(float(chart.planets[Planet.SUN].longitude))  # 15° Libra – 15° Scorpio

phase = compute_moon_phase(chart)  # quarter (1–4 by elongation) + waxing flag

siege = chart_besiegement(chart, Planet.MOON)
# .bodily      — nearest bodies on both zodiacal sides are Mars and Saturn
#                (Lilly CA I p.113), with arcs to each
# .by_rays     — separating from one malefic, applying to the other
#                (+ .benefic_intervention when an applying benefic perfects first)

voc = chart_void_of_course(chart)
# Void when no Ptolemaic aspect PERFECTS before the Moon leaves its sign
# (perfection criterion; classical static approximation). When not void,
# .next_perfection carries the planet, aspect angle, and arc to exactness.
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

Each `PlanetPosition` also exposes the **rulers of the segment** it falls
in — handy without an extra lookup:

```python
sun.face_ruler          # Chaldean-decan ruler (10° segment)
sun.term_ruler          # Egyptian term ruler (call term_of() for other systems)
sun.triplicity_rulers   # TriplicityRulers(day, night, participating)
sun.monomoira_ruler     # per-degree ruler at this longitude

# Sect-aware triplicity ruler:
tri_ruler = sun.triplicity_rulers.day if chart.is_diurnal else sun.triplicity_rulers.night
```

These describe the zodiacal segment, not the body — the face ruler at
0° Aries is Mars whether the position is occupied by the Sun, Saturn, or
a node. They are also surfaced in `Chart.to_dict()` for serialisation.

### Numeric dignity score (Lilly weights)

```python
from astrologica import LILLY_WEIGHTS, Planet, dignity_score

# Mars at 0° Aries: domicile (+5) + face (+1) = 6.
score = dignity_score(Planet.MARS, 0.0, is_diurnal=True, weights=LILLY_WEIGHTS)
```

Pass your own `EssentialWeights(domicile=..., exaltation=..., ...)` to use a different scheme.

### Almuten Figuris

```python
from astrologica import compute_almuten_figuris

result = compute_almuten_figuris(chart)
print(result.winner)            # the winning planet, or None on dead heat
print(result.runners_up)        # tied/close runners after tie-break trace
print(result.totals)            # full per-planet score breakdown
for b in result.breakdown:
    print(b.point.label, b.per_planet)
```

The result also exposes split scoring — `essential_totals` (dignity
points), `accidental_totals` (house-quality weights), and
`modifier_totals` (state bonuses/penalties) — plus `tie_break_trace`
explaining how the winner was selected. For an arbitrary point set, use
`compute_almuten(chart, points=[AlmutenPoint("MyLot", lon)], ...)`.

**Custom weights and modifiers.** Pass `essential_weights`,
`accidental_weights`, or `modifiers` to override defaults:

```python
from astrologica import (
    AlmutenModifiers, EssentialWeights, HouseQuality,
    compute_almuten_figuris,
)

result = compute_almuten_figuris(
    chart,
    essential_weights=EssentialWeights(
        domicile=5, exaltation=4, triplicity=3, term=2, face=1,
    ),
    accidental_weights={
        HouseQuality.ANGULAR: 4,
        HouseQuality.SUCCEDENT: 2,
        HouseQuality.CADENT: 0,
    },
    modifiers=AlmutenModifiers(
        combust=-5, under_beams=-4, cazimi=+5, retrograde=-5,
        aversion_to_asc=-2, oriental_bonus_superior=+2,
        occidental_bonus_inferior=+2, fast_or_direct_bonus=+1,
        angular_house=+5, succedent_house=+3, cadent_house=+0,
        malefic_in_6_or_12=-4,
    ),
)
```

### Firdaria

```python
from astrologica import FirdariaTradition, compute_firdaria

periods = compute_firdaria(chart, tradition=FirdariaTradition.AL_BIRUNI)
for p in periods:
    print(f"{p.ruler.name}: ages {p.start_age:.1f}–{p.end_age:.1f}")
    for s in p.sub_periods:
        print(f"  {s.ruler.name}: {s.start_age:.2f}–{s.end_age:.2f}")
```

Each major period is split into seven sub-periods (1/7 of the major span)
cycling through the remaining six planets plus the major ruler itself.
Node periods (`TRUE_NODE`, `SOUTH_TRUE_NODE`) have no sub-periods. The
nocturnal sequence differs by tradition — `AL_BIRUNI` places the nodes at
the end (most common); `BONATTI` places them mid-sequence after Mars. The
diurnal sequence is identical in both.

### Decennials (Valens)

```python
from astrologica import compute_decennials

# Diurnal: Sun → Venus → Mercury → Moon → Saturn → Jupiter → Mars (Chaldean order from sect light)
# Nocturnal: Moon → Saturn → Jupiter → Mars → Sun → Venus → Mercury
# Each period is 10y9m (10.75y; 129 months); one full cycle of 7 = 75y3m.
# Each major period carries 7 sub-periods (~1y 6m 12d each).
for p in compute_decennials(chart, max_age_years=82.0):
    print(f"{p.ruler.name}: ages {p.start_age}–{p.end_age}")
    for s in p.sub_periods:
        print(f"  {s.ruler.name}: {s.start_age:.2f}–{s.end_age:.2f}")
```

### Annual profection (Ptolemaic 12-house cycle)

```python
from astrologica import compute_annual_profection

p = compute_annual_profection(chart, age_years=29)
print(p.profected_house, p.profected_sign.name, p.lord_of_year.name)
# year 0 → 1st house; the cycle repeats every 12 years.
```

### Term distribution (Naibod-directed Ascendant)

```python
from astrologica import compute_term_distribution

# Walk the Ascendant forward through term boundaries at the Naibod rate
# (≈0.986°/year). Each period's ruler is the Lord of that age-span.
for p in compute_term_distribution(chart, max_age_years=82.0):
    print(f"{p.ruler.name} ({p.sign.name}): ages {p.start_age:.1f}–{p.end_age:.1f}")
```

### Saturn return

```python
from astrologica import compute_saturn_return

first  = compute_saturn_return(chart, n=1)   # ≈ age 29.5
second = compute_saturn_return(chart, n=2)   # ≈ age 59
```

### Monomoira (per-degree ruler)

Each integer degree of the zodiac has a planetary ruler — the
*monomoira* — taken from a 360-row table. Useful as fine-grain dignity
data and as a tie-break in Almuten computations.

```python
from astrologica import MONOMOIRAI, monomoira_of

ruler = monomoira_of(0.0)        # → Planet.MARS (0° Aries)
ruler = monomoira_of(24.72)      # ruler of the 25th degree of Aries
# MONOMOIRAI is the full 360-tuple if you want to walk the table directly.
```

### Faces (decans), terms (bounds), triplicities

```python
from astrologica import (
    FACES, TRIPLICITY_BY_ELEMENT, face_of, term_boundaries, triplicity_of,
)
from astrologica.terms import TERMS_EGYPTIAN, TermsSystem
```

### Solar state, orientality, house quality, aversion

```python
from astrologica import (
    Angle, Planet, SOLAR_STATE_THRESHOLDS, SolarStateThresholds,
    planet_solar_state, planet_orientality,
    house_quality, is_in_aversion_to,
)

state = planet_solar_state(chart.planets[Planet.VENUS], chart.planets[Planet.SUN])
# → SolarState.CAZIMI / COMBUST / UNDER_BEAMS / FREE
ori   = planet_orientality(Planet.JUPITER, chart.planets)
# → Orientality.ORIENTAL / OCCIDENTAL (or None for luminaries)
hq    = house_quality(7)              # → HouseQuality.ANGULAR
av    = is_in_aversion_to(Planet.MARS, Angle.ASCENDANT, chart)

# Override thresholds (defaults: cazimi 17', combust 8.5°, under-beams 17°)
state = planet_solar_state(
    chart.planets[Planet.VENUS], chart.planets[Planet.SUN],
    thresholds=SolarStateThresholds(
        cazimi_arcminutes=17.0, combust_degrees=8.5, under_beams_degrees=17.0,
    ),
)
```

### Aspects to angles

```python
from astrologica import Angle, compute_aspects

aspects = compute_aspects(
    chart.planets,
    include_angles=(Angle.ASCENDANT, Angle.MIDHEAVEN),
    chart=chart,
)
```

### Optional nodes for traditional charts

```python
chart = compute_natal_chart(data, include_nodes=True)
# now chart.planets contains TRUE_NODE and SOUTH_TRUE_NODE
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

Threaded through the chart via `ChartConfig.terms_system` (see below):
`EGYPTIAN` (default), `PTOLEMAIC`, `CHALDEAN`, `DOROTHEAN`,
`ASTROLOGICAL_ASSOCIATION`. The chosen system drives every dignity-aware
computation in the chart — per-planet `dignities`, `term_ruler`, and
`almuten_figuris`.

### ChartConfig — editorial knobs

`compute_natal_chart` accepts a `config: ChartConfig` kwarg bundling every
editorial choice the chart makes. All defaults are Hellenistic-traditional,
so you can ignore it; override sub-configs to suit your scheme.

```python
from astrologica import (
    AlmutenConfig, AlmutenModifiers, ChartConfig, HouseQuality,
    TermsSystem, compute_natal_chart,
)

chart = compute_natal_chart(
    data,
    config=ChartConfig(
        terms_system=TermsSystem.PTOLEMAIC,
        almuten=AlmutenConfig(
            accidental_weights={
                HouseQuality.ANGULAR: 5,
                HouseQuality.SUCCEDENT: 3,
                HouseQuality.CADENT: 0,
            },
            modifiers=AlmutenModifiers(
                combust=-5, cazimi=+5, retrograde=-5,
                angular_house=+5, oriental_bonus_superior=+2,
            ),
            sect_aware=True,
        ),
    ),
)
chart.almuten_figuris.winner    # eagerly computed using the config
chart.config.terms_system       # echoed back for traceability
```

Adding new sub-configs (aspect orbs, solar-state thresholds, rulership
scheme) is purely additive — existing call sites won't break.

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
| `config` | `ChartConfig` | editorial knobs (terms system, almuten weights) |
| `house_system` | `HouseSystem` | the system used for cusps |
| `tradition` | `ChartTradition` | `TRADITIONAL` or `MODERN` body set |
| `ascendant`, `midheaven` | `Longitude` | angles |
| `is_diurnal` | `bool` | sect — Sun above horizon? |
| `syzygy` | `Syzygy` | prenatal lunation (kind / when / longitude / sign) |
| `planets` | `Mapping[Planet, PlanetPosition]` | per-body: position, speed, dignities, house, solar state, orientality, ruler properties |
| `houses` | `tuple[HouseCusp, ...]` | cusp longitudes |
| `aspects` | `tuple[Aspect, ...]` | Ptolemaic + semisextile + quincunx, including aspects to Asc/MC |
| `lots` | `Mapping[Lot, LotPosition]` | classical seven lots |
| `almuten_figuris` | `AlmutenResult` | chart's overall ruler, eagerly computed from `config.almuten` |

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
