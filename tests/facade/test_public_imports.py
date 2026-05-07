"""Guards against facade drift: every documented public import path must resolve."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.pure


class TestConceptFacades:
    def test_chart(self) -> None:
        from astrologica.chart import (  # noqa: F401
            Chart,
            ChartTradition,
            compute_natal_chart,
        )
        from astrologica.chart_data import (  # noqa: F401
            Ayanamsa,
            ChartData,
            ReferenceFrame,
        )

    def test_planet(self) -> None:
        from astrologica.planet import (  # noqa: F401
            Planet,
            PlanetPosition,
            compute_planet_positions,
        )

    def test_sign(self) -> None:
        from astrologica.sign import Sign  # noqa: F401

    def test_house(self) -> None:
        from astrologica.house import (  # noqa: F401
            House,
            HouseCusp,
            HouseSystem,
            compute_house_cusps,
        )

    def test_aspect(self) -> None:
        from astrologica.aspect import Aspect, AspectKind, compute_aspects  # noqa: F401

    def test_lot(self) -> None:
        from astrologica.lot import Lot, LotPosition, compute_lots  # noqa: F401

    def test_dignity(self) -> None:
        from astrologica.dignity import Dignity, compute_dignities  # noqa: F401

    def test_syzygy(self) -> None:
        from astrologica.syzygy import Syzygy, SyzygyKind, compute_prenatal_syzygy  # noqa: F401

    def test_diurnal(self) -> None:
        from astrologica.diurnal import compute_is_diurnal  # noqa: F401

    def test_antiscion(self) -> None:
        from astrologica.antiscion import (  # noqa: F401
            compute_antiscion,
            compute_contraantiscion,
        )

    def test_dodecatemorion(self) -> None:
        from astrologica.dodecatemorion import (  # noqa: F401
            DodecatemorionVariant,
            compute_dodecatemorion,
        )

    def test_faces(self) -> None:
        from astrologica.faces import FACES, face_of  # noqa: F401

    def test_terms(self) -> None:
        from astrologica.terms import (  # noqa: F401
            TERMS_EGYPTIAN,
            TermBoundary,
            term_boundaries,
            term_of,
        )

    def test_triplicities(self) -> None:
        from astrologica.triplicities import (  # noqa: F401
            TRIPLICITY_BY_ELEMENT,
            TriplicityRulers,
            triplicity_of,
        )

    def test_monomoirai(self) -> None:
        from astrologica.monomoirai import MONOMOIRAI, monomoira_of  # noqa: F401

    def test_solar_state(self) -> None:
        from astrologica.solar_state import (  # noqa: F401
            SOLAR_STATE_THRESHOLDS,
            SolarState,
            SolarStateThresholds,
            planet_solar_state,
        )

    def test_orientality(self) -> None:
        from astrologica.orientality import Orientality, planet_orientality  # noqa: F401

    def test_almuten(self) -> None:
        from astrologica.almuten import (  # noqa: F401
            DEFAULT_ALMUTEN_MODIFIERS,
            AlmutenModifiers,
            AlmutenPoint,
            AlmutenResult,
            compute_almuten,
            compute_almuten_figuris,
        )

    def test_firdaria(self) -> None:
        from astrologica.firdaria import (  # noqa: F401
            FirdariaPeriod,
            FirdariaTradition,
            compute_firdaria,
        )

    def test_house_quality(self) -> None:
        from astrologica.house import HouseQuality, house_quality  # noqa: F401

    def test_dignity_score(self) -> None:
        from astrologica.dignity import (  # noqa: F401
            LILLY_WEIGHTS,
            EssentialWeights,
            dignity_score,
        )

    def test_aspect_extensions(self) -> None:
        from astrologica.aspect import (  # noqa: F401
            DEFAULT_ORBS,
            LUMINARY_ORB_BONUS,
            Angle,
            AspectEndpoint,
            default_orb,
            is_in_aversion_to,
        )


class TestMeasureFacades:
    def test_place(self) -> None:
        from astrologica.place import Place  # noqa: F401

    def test_angle(self) -> None:
        from astrologica.angle import Degree, Latitude, Longitude, Orb  # noqa: F401

    def test_ecliptic(self) -> None:
        from astrologica.ecliptic import EclipticPosition, Speed  # noqa: F401


class TestPortAndAdapterFacades:
    def test_ephemeris_port(self) -> None:
        from astrologica.ephemeris import EphemerisPort, RawHouseCusps  # noqa: F401

    def test_swiss_adapter(self) -> None:
        from astrologica.swisseph import SwissEphemerisAdapter  # noqa: F401


class TestOneStopFacade:
    def test_star_import_from_package_root(self) -> None:
        import astrologica

        # All these names must be re-exported at the package top level.
        for name in (
            "Aspect",
            "AspectKind",
            "Ayanamsa",
            "Chart",
            "ChartData",
            "ChartTradition",
            "Dignity",
            "DodecatemorionVariant",
            "EclipticPosition",
            "EphemerisPort",
            "House",
            "HouseCusp",
            "HouseSystem",
            "Latitude",
            "Longitude",
            "Lot",
            "LotPosition",
            "Orb",
            "Place",
            "Planet",
            "PlanetPosition",
            "RawHouseCusps",
            "ReferenceFrame",
            "Sign",
            "Speed",
            "SwissEphemerisAdapter",
            "Syzygy",
            "SyzygyKind",
            "compute_antiscion",
            "compute_aspects",
            "compute_contraantiscion",
            "compute_dignities",
            "compute_dodecatemorion",
            "compute_house_cusps",
            "compute_is_diurnal",
            "compute_lots",
            "compute_natal_chart",
            "compute_planet_positions",
            "compute_prenatal_syzygy",
            # Phase A 0.2.0 additions
            "AlmutenModifiers",
            "AlmutenPoint",
            "AlmutenResult",
            "Angle",
            "DEFAULT_ALMUTEN_MODIFIERS",
            "EssentialWeights",
            "FACES",
            "FirdariaPeriod",
            "FirdariaTradition",
            "HouseQuality",
            "LILLY_WEIGHTS",
            "MONOMOIRAI",
            "Orientality",
            "SolarState",
            "TERMS_EGYPTIAN",
            "TRIPLICITY_BY_ELEMENT",
            "compute_almuten",
            "compute_almuten_figuris",
            "compute_firdaria",
            "dignity_score",
            "face_of",
            "house_quality",
            "is_in_aversion_to",
            "monomoira_of",
            "planet_orientality",
            "planet_solar_state",
            "term_boundaries",
            "triplicity_of",
        ):
            assert hasattr(astrologica, name), f"astrologica.{name} is not re-exported"
