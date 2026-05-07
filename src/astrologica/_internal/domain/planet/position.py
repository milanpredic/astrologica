"""PlanetPosition — a planet's state at a specific moment."""

from __future__ import annotations

from dataclasses import dataclass, field

from astrologica._internal.domain.dignity.dignity import Dignity
from astrologica._internal.domain.measures.ecliptic import EclipticPosition
from astrologica._internal.domain.orientality.types import Orientality
from astrologica._internal.domain.planet.planet import Planet
from astrologica._internal.domain.sign import Sign
from astrologica._internal.domain.solar_state.types import SolarState
from astrologica._internal.domain.tables.faces import face_of
from astrologica._internal.domain.tables.monomoirai import monomoira_of
from astrologica._internal.domain.tables.terms import TermsSystem, term_of
from astrologica._internal.domain.tables.triplicities import TriplicityRulers, triplicity_of


@dataclass(frozen=True, slots=True)
class PlanetPosition:
    """A planet placed in a chart — identity, position, and chart-context state.

    The `dignities`, `house`, `solar_state`, and `orientality` fields are
    populated by `compute_natal_chart` from the surrounding chart state. When
    a `PlanetPosition` is constructed standalone (without chart context), the
    chart-derived fields default to None (or empty for `dignities`).

    `terms_system` records which terms table was used for dignity scoring and
    drives `term_ruler`. Defaults to Egyptian — the Hellenistic standard.
    """

    planet: Planet
    position: EclipticPosition
    dignities: frozenset[Dignity] = field(default_factory=frozenset)
    terms_system: TermsSystem = TermsSystem.EGYPTIAN
    house: int | None = None
    solar_state: SolarState | None = None
    orientality: Orientality | None = None

    @property
    def sign(self) -> Sign:
        return Sign.of(self.position.longitude)

    @property
    def degree_in_sign(self) -> float:
        return Sign.degree_in(self.position.longitude)

    @property
    def is_retrograde(self) -> bool:
        return self.position.speed.is_retrograde

    @property
    def longitude(self) -> float:
        return float(self.position.longitude)

    @property
    def face_ruler(self) -> Planet:
        """Chaldean-decan ruler of the 10° segment this position falls in."""
        return face_of(self.sign, self.degree_in_sign)

    @property
    def term_ruler(self) -> Planet:
        """Term (bound) ruler under this position's `terms_system`."""
        return term_of(self.sign, self.degree_in_sign, system=self.terms_system)

    @property
    def triplicity_rulers(self) -> TriplicityRulers:
        """Day, night, and participating triplicity rulers for this position's sign.

        Pick by chart sect: `pp.triplicity_rulers.day if chart.is_diurnal else .night`.
        """
        return triplicity_of(self.sign)

    @property
    def monomoira_ruler(self) -> Planet:
        """Per-degree (monomoira) ruler at this position's longitude."""
        return monomoira_of(self.longitude)
