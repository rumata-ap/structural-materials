"""Нормативная библиотека строительных материалов (СП 15.13330, СП 16.13330, СП 63.13330, СП 64.13330)."""

import sys

from . import sp15_materials
from . import sp16_materials
from . import sp63_materials
from . import sp64_materials

# Короткие псевдонимы модулей
sp15 = sp15_materials
sp16 = sp16_materials
sp63 = sp63_materials
sp64 = sp64_materials

# Экспорт основных классов
from .sp15_materials import Masonry, ReinforcedMasonry
from .sp16_materials import StructuralSteel, SteelBolt
from .sp63_materials import Concrete, Rebar
from .sp64_materials import (
    Timber,
    StrengthClassWood,
    Glulam,
    LVL,
    Plywood,
    OSB3,
    WoodContext,
)

# Регистрация псевдонимов в sys.modules для поддержки обратной совместимости
sys.modules.setdefault("sp15_materials", sp15_materials)
sys.modules.setdefault("sp16_materials", sp16_materials)
sys.modules.setdefault("sp63_materials", sp63_materials)
sys.modules.setdefault("sp64_materials", sp64_materials)

__version__ = "0.3.0"

__all__ = [
    "sp15",
    "sp16",
    "sp63",
    "sp64",
    "sp15_materials",
    "sp16_materials",
    "sp63_materials",
    "sp64_materials",
    "Masonry",
    "ReinforcedMasonry",
    "StructuralSteel",
    "SteelBolt",
    "Concrete",
    "Rebar",
    "Timber",
    "StrengthClassWood",
    "Glulam",
    "LVL",
    "Plywood",
    "OSB3",
    "WoodContext",
]

