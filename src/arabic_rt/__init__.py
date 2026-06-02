# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""arabic-rt — Arabic shaping, BiDi, and un-baking for games, TTS, and real-time clients.

Quick start::

    import arabic_rt as ar

    baked = ar.fix("مرحبا بالعالم")     # -> visual-order presentation forms
    ar.unfix(baked)                      # -> back to logical "مرحبا بالعالم"
    ar.shape("سلم")                      # contextual shaping only (no reorder)

For naive game chat (word-by-word readers)::

    ar.fix("مرحبا بالعالم", ar.GAME)
"""
from __future__ import annotations

from ._engine import (
    Options,
    GAME,
    shape,
    fix,
    unfix,
    contains_arabic,
    is_shaped,
)

__version__ = "0.1.0"
__author__ = "Bandar AlSwyan"
__license__ = "MPL-2.0"

__all__ = [
    "Options",
    "GAME",
    "shape",
    "fix",
    "unfix",
    "contains_arabic",
    "is_shaped",
    "__version__",
]
