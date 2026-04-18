"""compute_rising_times — rising times of the 12 signs at a geographic latitude.

For each zodiac sign, return the ascensional time (in degrees of right ascension)
required for the sign to fully rise above the eastern horizon. The sum of all
12 rising times is 360° (a full sidereal day).

At latitude 0° (equator), every sign rises in exactly 30°. Away from the
equator, long-ascension signs (signs of Cancer through Sagittarius in the
Northern Hemisphere; Capricorn through Gemini in the Southern) rise slowly
and short-ascension signs rise quickly.

Formulas follow Ptolemaic / Almagest conventions:

    AD(λ, φ) = arcsin(tan(φ) · tan(δ(λ)))
    sign_rising_time = 30° ± Δ(AD)

where `δ(λ)` is the declination of the sign's beginning and end (approximated
via the ecliptic obliquity ε = 23.4392911° at J2000).
"""

from __future__ import annotations

import math
from collections.abc import Mapping

from astrologica._internal.domain.sign import Sign

_OBLIQUITY_DEG = 23.4392911  # mean obliquity at J2000.0


def _right_ascension(longitude_deg: float) -> float:
    """Right ascension of an ecliptic longitude on the celestial sphere.

    RA = atan2(cos(ε) · sin(λ), cos(λ)); returned in [0, 360).
    """
    lam = math.radians(longitude_deg)
    eps = math.radians(_OBLIQUITY_DEG)
    ra_rad = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    return math.degrees(ra_rad) % 360.0


def _declination(longitude_deg: float) -> float:
    """Declination of an ecliptic longitude: δ = arcsin(sin(ε) · sin(λ))."""
    lam = math.radians(longitude_deg)
    eps = math.radians(_OBLIQUITY_DEG)
    return math.degrees(math.asin(math.sin(eps) * math.sin(lam)))


def _ascensional_difference(latitude_deg: float, declination_deg: float) -> float:
    """Ascensional difference AD(φ, δ) = arcsin(tan(φ) · tan(δ)).

    Returns NaN near the polar circle where the argument exceeds 1 in abs value.
    """
    phi = math.radians(latitude_deg)
    delta = math.radians(declination_deg)
    arg = math.tan(phi) * math.tan(delta)
    if abs(arg) > 1.0:
        return float("nan")
    return math.degrees(math.asin(arg))


def compute_rising_times(latitude_deg: float) -> Mapping[Sign, float]:
    """Return the rising time (°RA) for each of the 12 signs at `latitude_deg`.

    The rising time of a sign is the right-ascension span between its
    starting and ending points on the horizon: RA(end) − RA(start), adjusted
    for the ascensional difference at the observer's latitude.

    At latitude 0 the sum is exactly 360° and every sign rises in 30°.
    """
    result: dict[Sign, float] = {}
    for sign in Sign:
        lon_start = sign.value * 30.0
        lon_end = lon_start + 30.0
        ra_start = _right_ascension(lon_start)
        ra_end = _right_ascension(lon_end)

        ad_start = _ascensional_difference(latitude_deg, _declination(lon_start))
        ad_end = _ascensional_difference(latitude_deg, _declination(lon_end))

        # Oblique ascension: OA = RA − AD. Rising time = OA(end) − OA(start).
        if math.isnan(ad_start) or math.isnan(ad_end):
            result[sign] = float("nan")
            continue

        oa_start = (ra_start - ad_start) % 360.0
        oa_end = (ra_end - ad_end) % 360.0
        rising_time = (oa_end - oa_start) % 360.0
        result[sign] = rising_time
    return result
