"""Public facade for the custom lot builder.

Declarative DSL for defining arbitrary Hellenistic / Arabic parts beyond
the classical seven. Example — the Lot of Fortune rebuilt as a custom lot:

```python
fortune = CustomLot(
    name="Fortune",
    day=LotFormula(plus=(Planet.MOON,), minus=(Planet.SUN,)),
    night=LotFormula(plus=(Planet.SUN,), minus=(Planet.MOON,)),
)
lon = compute_custom_lot(chart, fortune)
```

ASC is implicitly added to every formula — you specify only the non-ASC
parts. The `day` formula applies for diurnal charts and `night` for nocturnal
(sect inversion is done here automatically).
"""

from __future__ import annotations

from astrologica._internal.domain.custom_lot import (
    CardinalAngle,
    CustomLot,
    HouseCuspRef,
    LordOf,
    LotComponent,
    LotFormula,
    PriorLot,
    RulerOf,
    SyzygyPoint,
    compute_custom_lot,
)
from astrologica._internal.domain.custom_lot.component import (
    CardinalAngleName,
    LordKind,
    RulerOfKind,
)

__all__ = [
    "CardinalAngle",
    "CardinalAngleName",
    "CustomLot",
    "HouseCuspRef",
    "LordKind",
    "LordOf",
    "LotComponent",
    "LotFormula",
    "PriorLot",
    "RulerOf",
    "RulerOfKind",
    "SyzygyPoint",
    "compute_custom_lot",
]
