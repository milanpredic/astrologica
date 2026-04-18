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
        ):
            assert hasattr(astrologica, name), f"astrologica.{name} is not re-exported"
