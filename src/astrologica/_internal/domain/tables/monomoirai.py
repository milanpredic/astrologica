"""Per-degree (monomoira) planet rulers — bundled CSV lookup.

Loaded once at import from `astrologica._data/monomoira.csv`. The CSV uses
English sign names (Aries, Taurus, …) and 3-letter planet abbreviations
(Sat, Jup, Mars, Sun, Ven, Mer, Moon).
"""

from __future__ import annotations

import csv
from importlib import resources

from astrologica._internal.domain.measures.angle import normalize_longitude
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign

_PLANET_ABBR: dict[str, Planet] = {
    "Sat": Planet.SATURN,
    "Jup": Planet.JUPITER,
    "Mars": Planet.MARS,
    "Sun": Planet.SUN,
    "Ven": Planet.VENUS,
    "Mer": Planet.MERCURY,
    "Moon": Planet.MOON,
}

_SIGN_NAME: dict[str, Sign] = {
    "Aries": Sign.ARIES,
    "Taurus": Sign.TAURUS,
    "Gemini": Sign.GEMINI,
    "Cancer": Sign.CANCER,
    "Leo": Sign.LEO,
    "Virgo": Sign.VIRGO,
    "Libra": Sign.LIBRA,
    "Scorpio": Sign.SCORPIO,
    "Sagittarius": Sign.SAGITTARIUS,
    "Capricorn": Sign.CAPRICORN,
    "Aquarius": Sign.AQUARIUS,
    "Pisces": Sign.PISCES,
}


def _load() -> dict[Sign, tuple[Planet, ...]]:
    csv_text = (
        resources.files("astrologica._data").joinpath("monomoira.csv").read_text(encoding="utf-8")
    )
    reader = csv.reader(csv_text.splitlines())
    rows = list(reader)
    if not rows or len(rows) < 13:
        raise RuntimeError(f"monomoira.csv malformed: expected header + 12 rows, got {len(rows)}")
    out: dict[Sign, tuple[Planet, ...]] = {}
    for row in rows[1:]:
        if not row:
            continue
        sign_name, *cells = row
        sign = _SIGN_NAME.get(sign_name)
        if sign is None:
            raise RuntimeError(f"monomoira.csv: unknown sign {sign_name!r}")
        if len(cells) != 30:
            raise RuntimeError(f"monomoira.csv: {sign_name} has {len(cells)} cells, expected 30")
        out[sign] = tuple(_PLANET_ABBR[abbr.strip()] for abbr in cells)
    if set(out.keys()) != set(Sign):
        missing = set(Sign) - set(out.keys())
        raise RuntimeError(f"monomoira.csv missing signs: {missing}")
    return out


MONOMOIRAI: dict[Sign, tuple[Planet, ...]] = _load()


def monomoira_of(longitude: float) -> Planet:
    """Per-degree (per-stepenski) planet ruler for any ecliptic longitude.

    Uses degree-floor lookup: the integer part of `longitude % 30` indexes
    into the row for the sign. Negative and out-of-range longitudes are
    normalized to [0, 360).
    """
    norm = normalize_longitude(longitude)
    sign = Sign.of(norm)
    degree_in = int(norm - float(int(sign)) * 30.0)
    if degree_in == 30:
        degree_in = 29
    return MONOMOIRAI[sign][degree_in]
