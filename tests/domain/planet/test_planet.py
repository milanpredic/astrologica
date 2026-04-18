"""Planet enum — classical vs modern membership and classification predicates."""

from __future__ import annotations

from astrologica._internal.domain.planet.planet import Planet


class TestPlanetMembership:
    def test_has_seven_classical_planets(self) -> None:
        classical = Planet.classical()
        assert classical == frozenset(
            {
                Planet.SUN,
                Planet.MOON,
                Planet.MERCURY,
                Planet.VENUS,
                Planet.MARS,
                Planet.JUPITER,
                Planet.SATURN,
            }
        )

    def test_has_three_outer_planets(self) -> None:
        outers = {Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO}
        for p in outers:
            assert p.is_outer

    def test_has_four_node_members(self) -> None:
        nodes = {
            Planet.TRUE_NODE,
            Planet.MEAN_NODE,
            Planet.SOUTH_TRUE_NODE,
            Planet.SOUTH_MEAN_NODE,
        }
        for n in nodes:
            assert n.is_node

    def test_modern_set_is_superset_of_classical(self) -> None:
        assert Planet.classical() <= Planet.modern()

    def test_modern_set_is_13_bodies(self) -> None:
        assert len(Planet.modern()) == 14
        # 7 classical + 3 outer + 4 nodes = 14


class TestClassificationPredicates:
    def test_luminary_is_only_sun_and_moon(self) -> None:
        for p in Planet:
            expected = p in (Planet.SUN, Planet.MOON)
            assert p.is_luminary is expected

    def test_classical_predicate(self) -> None:
        for p in Planet:
            assert p.is_classical == (p in Planet.classical())

    def test_outer_predicate_only_for_outer_planets(self) -> None:
        for p in Planet:
            expected = p in (Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO)
            assert p.is_outer is expected

    def test_node_predicate_only_for_nodes(self) -> None:
        nodes = {
            Planet.TRUE_NODE,
            Planet.MEAN_NODE,
            Planet.SOUTH_TRUE_NODE,
            Planet.SOUTH_MEAN_NODE,
        }
        for p in Planet:
            assert p.is_node == (p in nodes)

    def test_classical_and_outer_are_disjoint(self) -> None:
        for p in Planet:
            if p.is_classical:
                assert not p.is_outer
                assert not p.is_node

    def test_every_planet_is_exactly_one_category(self) -> None:
        for p in Planet:
            categories = sum([p.is_classical, p.is_outer, p.is_node])
            assert categories == 1, f"{p.name} must be in exactly one category, got {categories}"
