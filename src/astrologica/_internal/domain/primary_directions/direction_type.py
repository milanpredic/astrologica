"""DirectionType — DIRECT or CONVERSE primary direction.

A DIRECT direction moves the promissor forward (with the diurnal rotation)
to the significator's position. A CONVERSE direction moves the significator
forward to the promissor. Both are legitimate under traditional rules;
converse directions are typically read as past events or "shadow" themes.
"""

from __future__ import annotations

from enum import Enum


class DirectionType(Enum):
    DIRECT = "direct"
    CONVERSE = "converse"
