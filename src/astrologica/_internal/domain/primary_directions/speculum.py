"""Placidian speculum — per-body astronomical data needed for primary directions.

For each body in a chart, the speculum captures the full set of positional
quantities Placidian / Ptolemaic primary directions depend on:

- Ecliptic longitude + latitude
- Right ascension (RA) + declination
- Ascensional difference at the birth latitude (AD_lat)
- Semi-arc (SA) — diurnal if above the horizon, nocturnal if below
- Meridian distance (MD) — distance from MC (diurnal) or IC (nocturnal)
- Horizon distance (HD) — shortest arc to ASC or DSC, signed
- Temporal hour (TH = SA / 6)
- Hourly distance (HOD = MD / TH)
- Placidian mundane position (PMP) in [0°, 360°) around the observer's dome
- Ascensional difference at the body's pole height (AD_ph)
- Pole height (POH) — the latitude at which the body's semi-arc equals 90°
- Oblique ascension / descension (AO_DO) — signed: positive for eastern (AO),
  negative for western (DO)
- Orientation flags: `is_eastern` and `is_above_horizon`

Formulas follow Valens' `placspec.py` (Ptolemy/Placidus tradition).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass

from astrologica._internal.domain.chart.chart import Chart
from astrologica._internal.domain.planet.planet import Planet

_OBLIQUITY_DEG = 23.4392911


@dataclass(frozen=True, slots=True)
class Speculum:
    """Placidian speculum: per-body astronomical state for primary directions.

    Signs follow Valens' convention:
    - `sa` is positive for diurnal bodies (above horizon) and negative for
      nocturnal (below horizon).
    - `md` is signed with the same rule — positive from MC if above, negative
      from IC if below.
    - `hd` is negative when the body is closer to the DSC than to the ASC.
    - `ao_do` is positive for an Eastern body (ascensional side; AO), negative
      for Western (descensional; DO).
    """

    body: Planet
    lon: float
    lat: float
    ra: float
    decl: float
    ad_lat: float
    sa: float
    md: float
    hd: float
    th: float
    hod: float
    pmp: float
    ad_ph: float
    poh: float
    ao_do: float
    is_eastern: bool
    is_above_horizon: bool


def _ra_decl(longitude_deg: float, latitude_deg: float = 0.0) -> tuple[float, float]:
    """Convert ecliptic (longitude, latitude) → (RA, declination) in degrees."""
    lam = math.radians(longitude_deg)
    beta = math.radians(latitude_deg)
    eps = math.radians(_OBLIQUITY_DEG)

    sin_delta = math.sin(beta) * math.cos(eps) + math.cos(beta) * math.sin(eps) * math.sin(lam)
    decl = math.degrees(math.asin(sin_delta))

    ra_rad = math.atan2(
        math.sin(lam) * math.cos(eps) - math.tan(beta) * math.sin(eps),
        math.cos(lam),
    )
    return math.degrees(ra_rad) % 360.0, decl


def compute_speculum(body: Planet, chart: Chart) -> Speculum:
    """Compute the Placidian speculum for `body` in `chart`."""
    pp = chart.planets[body]
    lon = float(pp.longitude)
    lat = float(pp.position.latitude)
    place_lat = chart.data.place.latitude

    ra, decl = _ra_decl(lon, lat)

    # RAMC / RAIC from the chart's MC longitude.
    ramc, _ = _ra_decl(float(chart.midheaven), 0.0)
    raic = (ramc + 180.0) % 360.0

    # Eastern / western determination. Eastern hemisphere = RA on the ASC side
    # of the meridian (between IC and MC going counterclockwise through ASC).
    if ramc > raic:
        eastern = not (raic < ra < ramc)
    else:
        eastern = not (ra > raic or ra < ramc)

    # Ascensional difference at the birth latitude.
    tan_arg = math.tan(math.radians(place_lat)) * math.tan(math.radians(decl))
    ad_lat = math.degrees(math.asin(tan_arg)) if abs(tan_arg) <= 1.0 else 0.0

    # Meridian distances relative to MC and IC (shortest arc).
    med = abs(ramc - ra)
    if med > 180.0:
        med = 360.0 - med
    icd = abs(raic - ra)
    if icd > 180.0:
        icd = 360.0 - icd

    # Semi-arcs.
    dsa = 90.0 + ad_lat
    nsa = 90.0 - ad_lat

    above_horizon = med <= dsa
    if above_horizon:
        sa = dsa
        md_signed = med
    else:
        sa = -nsa  # negative marks nocturnal
        md_signed = -icd

    # Horizon distance: shortest-signed arc to either ASC or DSC.
    aoasc = (ramc + 90.0) % 360.0
    dodesc = (raic + 90.0) % 360.0

    aohd = ra - ad_lat
    hdasc = abs(aohd - aoasc)
    if hdasc > 180.0:
        hdasc = 360.0 - hdasc

    dohd = ra + ad_lat
    hddesc = abs(dohd - dodesc)
    if hddesc > 180.0:
        hddesc = 360.0 - hddesc

    hd = hdasc if hddesc >= hdasc else -hddesc

    # Temporal hour and hourly distance.
    th = sa / 6.0
    hod = md_signed / abs(th) if th != 0.0 else 0.0

    # Placidian mundane position — a 0–360° coordinate around the observer's
    # dome that stays continuous across quadrants.
    abs_md = abs(md_signed)
    abs_sa = abs(sa)
    md_ratio = abs_md / abs_sa if abs_sa != 0.0 else 0.0

    if not above_horizon and eastern:
        pmp = 90.0 - 90.0 * md_ratio
    elif not above_horizon and not eastern:
        pmp = 90.0 + 90.0 * md_ratio
    elif above_horizon and not eastern:
        pmp = 270.0 - 90.0 * md_ratio
    else:  # above_horizon and eastern
        pmp = 270.0 + 90.0 * md_ratio

    # AD at the body's pole height. AD_ph = |MD| * AD_lat / |SA|.
    ad_ph = abs_md * ad_lat / abs_sa if abs_sa != 0.0 else 0.0

    # Pole height: tan(phi) = sin(AD_ph) / tan(decl). When decl is 0 the body
    # has no meaningful pole — report 0.
    tan_decl = math.tan(math.radians(decl))
    poh = (
        math.degrees(math.atan(math.sin(math.radians(ad_ph)) / tan_decl))
        if tan_decl != 0.0
        else 0.0
    )

    # Oblique ascension / descension.
    if eastern:
        ao_do = ra - ad_ph
    else:
        ao_do = -(ra + ad_ph)  # negative marks DO (descensional)

    return Speculum(
        body=body,
        lon=lon,
        lat=lat,
        ra=ra,
        decl=decl,
        ad_lat=ad_lat,
        sa=sa,
        md=md_signed,
        hd=hd,
        th=th,
        hod=hod,
        pmp=pmp,
        ad_ph=ad_ph,
        poh=poh,
        ao_do=ao_do,
        is_eastern=eastern,
        is_above_horizon=above_horizon,
    )


def compute_all_specula(chart: Chart) -> Mapping[Planet, Speculum]:
    """Compute the speculum for every body in `chart`."""
    return {p: compute_speculum(p, chart) for p in chart.planets}


__all__ = ["Speculum", "compute_all_specula", "compute_speculum"]
