"""lookup_city — resolve city name to Place."""

from __future__ import annotations

import pytest

from astrologica.geo.place_lookup import lookup_city
from astrologica.place import Place


class TestLookupCity:
    def test_new_york(self) -> None:
        place = lookup_city("New York")
        assert isinstance(place, Place)
        # New York City is at roughly 40.7 N, -74.0 W.
        assert 40.0 <= place.latitude <= 41.5
        assert -75.0 <= place.longitude <= -73.0

    def test_case_insensitive(self) -> None:
        assert lookup_city("new york") == lookup_city("NEW YORK")

    def test_unknown_city_raises(self) -> None:
        with pytest.raises(LookupError):
            lookup_city("NotACity-xyzzy")
