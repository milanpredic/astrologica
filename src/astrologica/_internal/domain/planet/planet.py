"""Planet enum — classical 7 + modern outer planets + lunar nodes.

The `Planet` enum is partitioned into three disjoint categories:

- **Classical** (7): Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn — the
  visible bodies of traditional astrology. These are the only ones with
  essential dignities, lot-defining roles, and traditional rulerships.
- **Outer** (3): Uranus, Neptune, Pluto — modern additions, present only in
  `ChartTradition.MODERN` charts.
- **Nodes** (4): True/Mean lunar nodes and their southern counterparts.
  South nodes are always exactly 180° from their corresponding north node.

Use `Planet.classical()` and `Planet.modern()` for body-set selection;
`is_classical` / `is_outer` / `is_node` / `is_luminary` for classification.
"""

from __future__ import annotations

from enum import Enum


class Planet(Enum):
    """The celestial bodies astrologica computes positions for."""

    # Classical (7)
    SUN = "sun"
    MOON = "moon"
    MERCURY = "mercury"
    VENUS = "venus"
    MARS = "mars"
    JUPITER = "jupiter"
    SATURN = "saturn"

    # Outer modern planets (3)
    URANUS = "uranus"
    NEPTUNE = "neptune"
    PLUTO = "pluto"

    # Lunar nodes (4) — True and Mean, plus their southern antipodes
    TRUE_NODE = "true_node"
    MEAN_NODE = "mean_node"
    SOUTH_TRUE_NODE = "south_true_node"
    SOUTH_MEAN_NODE = "south_mean_node"

    @property
    def is_luminary(self) -> bool:
        return self in (Planet.SUN, Planet.MOON)

    @property
    def is_classical(self) -> bool:
        return self in _CLASSICAL

    @property
    def is_outer(self) -> bool:
        return self in _OUTER

    @property
    def is_node(self) -> bool:
        return self in _NODES

    @classmethod
    def classical(cls) -> frozenset[Planet]:
        """The 7 classical planets — the default body set for traditional charts."""
        return _CLASSICAL

    @classmethod
    def modern(cls) -> frozenset[Planet]:
        """Classical + outer planets + all four lunar nodes."""
        return _MODERN


_CLASSICAL: frozenset[Planet] = frozenset(
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

_OUTER: frozenset[Planet] = frozenset({Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO})

_NODES: frozenset[Planet] = frozenset(
    {
        Planet.TRUE_NODE,
        Planet.MEAN_NODE,
        Planet.SOUTH_TRUE_NODE,
        Planet.SOUTH_MEAN_NODE,
    }
)

_MODERN: frozenset[Planet] = _CLASSICAL | _OUTER | _NODES
