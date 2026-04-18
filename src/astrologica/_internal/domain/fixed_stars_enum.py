"""FixedStar — 30 classical fixed stars as a curated enum.

These are the stars Valens ships in its desktop app — the traditional
set consulted in Hellenistic and medieval astrology. Each star is identified
symbolically here; the mapping to Swiss Ephemeris names lives in
`tables/fixed_stars.py` so the domain layer stays backend-agnostic.
"""

from __future__ import annotations

from enum import Enum


class FixedStar(Enum):
    """30 classical fixed stars consulted in traditional astrology."""

    ETA_TAURI = "eta_tauri"  # the Pleiades seven sisters
    ALDEBARAN = "aldebaran"  # eye of the Bull; royal star of the east
    ALGOL = "algol"  # demon star, Perseus
    ALAMAK = "alamak"  # Andromeda
    ANTARES = "antares"  # heart of the Scorpion; royal star of the west
    ARCTURUS = "arcturus"  # Boötes
    ASELLUS_AUSTRALIS = "asellus_australis"  # southern ass
    ASELLUS_BOREALIS = "asellus_borealis"  # northern ass
    ALKAID = "alkaid"  # tail of Ursa Major
    BETELGEUSE = "betelgeuse"  # shoulder of Orion
    ALPHA_CENTAURI = "alpha_centauri"  # Rigil Kentaurus
    CANOPUS = "canopus"  # Carina
    CASTOR = "castor"  # Gemini
    DENEBOLA = "denebola"  # tail of the Lion
    FOMALHAUT = "fomalhaut"  # mouth of the Southern Fish; royal of the south
    ALPHECCA = "alphecca"  # Corona Borealis
    MARKAB = "markab"  # Pegasus
    MIRACH = "mirach"  # Andromeda
    POLARIS = "polaris"  # pole star
    POLLUX = "pollux"  # Gemini
    PRAESEPE = "praesepe"  # beehive cluster, Cancer
    PROCYON = "procyon"  # Canis Minor
    REGULUS = "regulus"  # heart of the Lion; royal of the north
    RIGEL = "rigel"  # foot of Orion
    SIRIUS = "sirius"  # the Dog Star
    SPICA = "spica"  # Virgo
    UNUKALHAI = "unukalhai"  # heart of the Serpent
    VEGA = "vega"  # Lyra
    ZUBENELGENUBI = "zubenelgenubi"  # southern scale, Libra
    ZUBENESCHAMALI = "zubeneschamali"  # northern scale, Libra
