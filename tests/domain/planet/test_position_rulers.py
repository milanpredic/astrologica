"""Ruler properties on PlanetPosition — face / term / triplicity / monomoira."""

from __future__ import annotations

from astrologica._internal.domain.dignity.dignity import Dignity
from astrologica._internal.domain.measures.angle import Latitude, Longitude
from astrologica._internal.domain.measures.ecliptic import EclipticPosition, Speed
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.planet.position import PlanetPosition
from astrologica._internal.domain.sign import Element, Sign


def _pp(planet: Planet, lon: float) -> PlanetPosition:
    return PlanetPosition(
        planet=planet,
        position=EclipticPosition(
            longitude=Longitude(lon), latitude=Latitude(0.0), speed=Speed(1.0)
        ),
        dignities=frozenset(),
    )


class TestFaceRuler:
    def test_first_decan_of_aries_is_mars(self) -> None:
        # 0–9.99° Aries → Mars (Chaldean decan starting from Mars).
        assert _pp(Planet.SUN, 5.0).face_ruler is Planet.MARS

    def test_third_decan_of_pisces_is_mars(self) -> None:
        # 20–29.99° Pisces → Mars (last decan of the zodiac).
        assert _pp(Planet.MOON, 355.0).face_ruler is Planet.MARS

    def test_face_ruler_is_pure_function_of_longitude(self) -> None:
        # Two different planets at the same longitude get the same face ruler.
        assert _pp(Planet.SUN, 100.0).face_ruler is _pp(Planet.SATURN, 100.0).face_ruler


class TestTermRuler:
    def test_egyptian_first_term_of_aries_is_jupiter(self) -> None:
        # Egyptian: Aries 0–6° → Jupiter.
        assert _pp(Planet.MARS, 3.0).term_ruler is Planet.JUPITER

    def test_egyptian_last_term_of_aries_is_saturn(self) -> None:
        # Egyptian: Aries 25–30° → Saturn.
        assert _pp(Planet.SUN, 27.0).term_ruler is Planet.SATURN


class TestTriplicityRulers:
    def test_fire_sign_returns_dorothean_fire_rulers(self) -> None:
        # Aries (fire): day=Sun, night=Jupiter, participating=Saturn.
        rulers = _pp(Planet.SUN, 5.0).triplicity_rulers
        assert rulers.day is Planet.SUN
        assert rulers.night is Planet.JUPITER
        assert rulers.participating is Planet.SATURN

    def test_water_sign_returns_dorothean_water_rulers(self) -> None:
        # Cancer (water): day=Venus, night=Mars, participating=Moon.
        rulers = _pp(Planet.MOON, 95.0).triplicity_rulers
        assert rulers.day is Planet.VENUS
        assert rulers.night is Planet.MARS
        assert rulers.participating is Planet.MOON

    def test_rulers_match_sign_element(self) -> None:
        # Every position's triplicity rulers come from its sign's element.
        for lon in (0.0, 35.0, 75.0, 130.0, 195.0, 250.0, 305.0):
            pp = _pp(Planet.SUN, lon)
            assert pp.sign.element in Element


class TestMonomoiraRuler:
    def test_first_degree_of_aries_is_mars(self) -> None:
        # The 0° (1st degree) of Aries: Mars.
        assert _pp(Planet.SUN, 0.0).monomoira_ruler is Planet.MARS

    def test_normalises_out_of_range_longitude(self) -> None:
        # Longitude past 360° wraps via the underlying monomoira_of.
        wrapped = _pp(Planet.SUN, 360.5).monomoira_ruler
        original = _pp(Planet.SUN, 0.5).monomoira_ruler
        assert wrapped is original


class TestRulersAreIndependentOfPlanetIdentity:
    def test_ruler_describes_segment_not_body(self) -> None:
        # A node sitting at 0° Aries gets the same face/term/monomoira rulers
        # as the Sun at 0° Aries — these properties describe the zodiac, not the body.
        sun_at_aries = _pp(Planet.SUN, 0.5)
        node_at_aries = _pp(Planet.TRUE_NODE, 0.5)
        assert sun_at_aries.face_ruler is node_at_aries.face_ruler
        assert sun_at_aries.term_ruler is node_at_aries.term_ruler
        assert sun_at_aries.monomoira_ruler is node_at_aries.monomoira_ruler


class TestDignitiesStillWork:
    def test_dignities_field_unaffected_by_new_properties(self) -> None:
        # Sanity check: we didn't break the existing dignities field.
        pp = PlanetPosition(
            planet=Planet.SUN,
            position=EclipticPosition(
                longitude=Longitude(120.0), latitude=Latitude(0.0), speed=Speed(1.0)
            ),
            dignities=frozenset({Dignity.DOMICILE}),
        )
        assert Dignity.DOMICILE in pp.dignities
        assert pp.sign is Sign.LEO
