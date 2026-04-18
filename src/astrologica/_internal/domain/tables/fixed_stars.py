"""Catalog of 30 classical fixed stars (Valens' curation).

Each entry maps a `FixedStar` enum member to its first-column name in the
bundled `sefstars.txt` catalog (shipped at `src/astrologica/_data/`). Swiss
Ephemeris matches star names case-insensitively against that column.
"""

from __future__ import annotations

from astrologica._internal.domain.fixed_stars_enum import FixedStar

SWE_STAR_NAMES: dict[FixedStar, str] = {
    FixedStar.ETA_TAURI: "EtaTau",
    FixedStar.ALDEBARAN: "Aldebaran",
    FixedStar.ALGOL: "Algol",
    FixedStar.ALAMAK: "Alamak",
    FixedStar.ANTARES: "Antares",
    FixedStar.ARCTURUS: "Arcturus",
    FixedStar.ASELLUS_AUSTRALIS: "AsellusAustralis",
    FixedStar.ASELLUS_BOREALIS: "AsellusBorealis",
    FixedStar.ALKAID: "Alkaid",
    FixedStar.BETELGEUSE: "Betelgeuse",
    FixedStar.ALPHA_CENTAURI: "AlphaCentauri",
    FixedStar.CANOPUS: "Canopus",
    FixedStar.CASTOR: "Castor",
    FixedStar.DENEBOLA: "Denebola",
    FixedStar.FOMALHAUT: "Fomalhaut",
    FixedStar.ALPHECCA: "Alphecca",
    FixedStar.MARKAB: "Markab",
    FixedStar.MIRACH: "Mirach",
    FixedStar.POLARIS: "Polaris",
    FixedStar.POLLUX: "Pollux",
    FixedStar.PRAESEPE: "Praesepe",
    FixedStar.PROCYON: "Procyon",
    FixedStar.REGULUS: "Regulus",
    FixedStar.RIGEL: "Rigel",
    FixedStar.SIRIUS: "Sirius",
    FixedStar.SPICA: "Spica",
    FixedStar.UNUKALHAI: "Unukalhai",
    FixedStar.VEGA: "Vega",
    FixedStar.ZUBENELGENUBI: "Zubenelgenubi",
    FixedStar.ZUBENESCHAMALI: "Zubeneshamali",
}
