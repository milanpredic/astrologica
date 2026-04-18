"""Ayanamsa — sidereal-zodiac reference modes.

Swiss Ephemeris provides many sidereal modes (the `SIDM_*` constants). This
enum exposes the 21 classical/standard choices that Valens ships. When an
`Ayanamsa` is attached to a `ChartData`, all computed longitudes (planets +
house cusps) are sidereal rather than tropical.

The mapping to the concrete Swiss Ephemeris `SIDM_*` IDs lives in the
infrastructure layer — the domain only knows the symbolic names.
"""

from __future__ import annotations

from enum import Enum


class Ayanamsa(Enum):
    """Classical sidereal modes (tropical = absence of any `Ayanamsa`)."""

    FAGAN_BRADLEY = "fagan_bradley"
    LAHIRI = "lahiri"
    DELUCE = "deluce"
    RAMAN = "raman"
    USHASHASHI = "ushashashi"
    KRISHNAMURTI = "krishnamurti"
    DJWHAL_KHUL = "djwhal_khul"
    YUKTESHWAR = "yukteshwar"
    JN_BHASIN = "jn_bhasin"
    BABYL_KUGLER1 = "babyl_kugler1"
    BABYL_KUGLER2 = "babyl_kugler2"
    BABYL_KUGLER3 = "babyl_kugler3"
    BABYL_HUBER = "babyl_huber"
    BABYL_ETPSC = "babyl_etpsc"
    ALDEBARAN_15TAU = "aldebaran_15tau"
    HIPPARCHOS = "hipparchos"
    SASSANIAN = "sassanian"
    GALCENT_0SAG = "galcent_0sag"
    J2000 = "j2000"
    J1900 = "j1900"
    B1950 = "b1950"
