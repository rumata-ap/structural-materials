"""Материалы по СП 64.13330.2017 «Деревянные конструкции».

Модуль содержит только свойства материалов и коэффициенты условий работы.
Расчёт элементов, соединений, огнезащиты и температурно-влажностных полей
намеренно не входит в этот слой библиотеки.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, ClassVar, Mapping


SOURCE_REVISION = "СП 64.13330.2017 (ред. от 28.12.2023, Изменения № 1–4)"

STRESS_NAMES = (
    "bending",
    "tension_parallel",
    "compression_parallel",
    "tension_perpendicular",
    "compression_perpendicular",
    "shear_parallel",
    "shear_perpendicular",
)

_STRESS_DISPLAY = {
    "bending": "изгиб",
    "tension_parallel": "растяжение вдоль волокон",
    "compression_parallel": "сжатие вдоль волокон",
    "tension_perpendicular": "растяжение поперёк волокон",
    "compression_perpendicular": "сжатие поперёк волокон",
    "shear_parallel": "скалывание вдоль волокон",
    "shear_perpendicular": "скалывание поперёк волокон",
}

SERVICE_CLASSES = ("1а", "1б", "2", "3", "4а", "4б")
LOAD_DURATION_MODES = ("А", "Б", "В", "Г", "Д", "Е", "Ж", "И", "К", "Л", "М")

_SERVICE_CLASS_ALIASES = {
    "1a": "1а",
    "1а": "1а",
    "1б": "1б",
    "1b": "1б",
    "2": "2",
    "3": "3",
    "4a": "4а",
    "4а": "4а",
    "4б": "4б",
    "4b": "4б",
}
_LOAD_DURATION_ALIASES = {
    "A": "А",
    "А": "А",
    "Б": "Б",
    "B": "В",
    "В": "В",
    "G": "Г",
    "Г": "Г",
    "D": "Д",
    "Д": "Д",
    "E": "Е",
    "Е": "Е",
    "Zh": "Ж",
    "Ж": "Ж",
    "I": "И",
    "И": "И",
    "K": "К",
    "К": "К",
    "L": "Л",
    "Л": "Л",
    "M": "М",
    "М": "М",
}

_SERVICE_CLASS_FACTORS = {"1а": 1.0, "1б": 1.0, "2": 1.0, "3": 0.9, "4а": 0.85, "4б": 0.75}
_DURATION_FACTORS = {
    "А": 1.0,
    "Б": 0.9,
    "В": 0.8,
    "Г": 0.66,
    "Д": 0.6,
    "Е": 0.5,
    "Ж": 0.4,
    "И": 0.3,
    "К": 0.25,
    "Л": 0.2,
    "М": 0.1,
}
_DURATION_CROSS_FIBER = {"В", "Г", "К"}
_DURATION_COMPRESSION_PERPENDICULAR = {"Г", "Д", "Е", "Ж", "И", "К"}

MATERIAL_GAMMA = {
    "bending": 1.20,
    "compression_parallel": 1.15,
    "tension_parallel": 1.25,
    "shear_parallel": 1.25,
    "compression_perpendicular": 1.15,
    "tension_perpendicular": 1.40,
    "shear_perpendicular": 1.25,
}

_SPECIES = (
    "pine",
    "spruce",
    "fir",
    "cedar",
    "larch_european",
    "larch_other",
)
_SPECIES_ALIASES = {
    "pine": "pine",
    "сосна": "pine",
    "spruce": "spruce",
    "ель": "spruce",
    "fir": "fir",
    "пихта": "fir",
    "кедр": "cedar",
    "cedar": "cedar",
    "лиственница европейская": "larch_european",
    "larch_european": "larch_european",
    "лиственница прочая": "larch_other",
    "larch_other": "larch_other",
}


def _canonical_service_class(value: str) -> str:
    key = str(value).strip()
    result = _SERVICE_CLASS_ALIASES.get(key, _SERVICE_CLASS_ALIASES.get(key.lower()))
    if result is None:
        raise ValueError(f"Неизвестный класс эксплуатации: {value!r}")
    return result


def _canonical_load_duration(value: str) -> str:
    key = str(value).strip()
    result = _LOAD_DURATION_ALIASES.get(key, _LOAD_DURATION_ALIASES.get(key.upper()))
    if result is None:
        raise ValueError(f"Неизвестный режим нагружения: {value!r}")
    return result


def _canonical_stress(stress: str) -> str:
    key = str(stress).strip()
    if key not in STRESS_NAMES:
        raise ValueError(f"Неизвестный вид напряжённого состояния: {stress!r}")
    return key


def _canonical_species(value: str) -> str:
    key = str(value).strip()
    result = _SPECIES_ALIASES.get(key, _SPECIES_ALIASES.get(key.lower()))
    if result is None or result not in _SPECIES:
        raise ValueError(f"Неизвестная порода древесины: {value!r}")
    return result


def _interpolate_clamped(x: float, points: tuple[tuple[float, float], ...]) -> float:
    if x <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return points[-1][1]


@dataclass(frozen=True)
class WoodContext:
    """Условия работы материала по таблицам 4, 9, 13 и п. 6.9б СП 64."""

    load_duration: str
    service_class: str = "2"
    temperature_c: float = 20.0
    service_life_years: float = 50.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "load_duration", _canonical_load_duration(self.load_duration))
        object.__setattr__(self, "service_class", _canonical_service_class(self.service_class))
        if self.temperature_c > 50:
            raise ValueError("Температура свыше 50 °C не поддерживается п. 6.9б СП 64")
        if self.service_life_years <= 0:
            raise ValueError("Срок службы должен быть положительным")

    @property
    def temperature_factor(self) -> float:
        return _interpolate_clamped(self.temperature_c, ((20.0, 1.0), (35.0, 1.0), (50.0, 0.8)))

    @property
    def duration_factor(self) -> float:
        return _DURATION_FACTORS[self.load_duration]

    @property
    def elastic_duration_factor(self) -> float:
        if self.load_duration == "Б":
            return 0.75
        if self.load_duration in {"В", "Г"}:
            return 0.9
        return 1.0

    @property
    def service_class_factor(self) -> float:
        return _SERVICE_CLASS_FACTORS[self.service_class]

    @property
    def service_class_display(self) -> str:
        return {
            "1а": "1а: сухие помещения",
            "1б": "1б: влажные помещения",
            "2": "2: влажные помещения / наружная защита",
            "3": "3: наружные конструкции под защитой",
            "4а": "4а: >20% влажности или >85% влажности воздуха",
            "4б": "4б: >20% / >85%",
        }[self.service_class]

    def m_service_life(self, stress: str) -> float:
        stress = _canonical_stress(stress)
        if stress in {"bending", "compression_parallel", "compression_perpendicular"}:
            terminal = (0.8,)
        elif stress in {"tension_parallel", "shear_parallel"}:
            terminal = (0.7,)
        else:
            terminal = (0.5,)
        return _interpolate_clamped(
            self.service_life_years,
            ((50.0, 1.0), (75.0, 0.9), (100.0, terminal[0])),
        )

    def factors(self, stress: str) -> dict[str, float]:
        stress = _canonical_stress(stress)
        cross_fiber = 0.9 if stress in {"tension_perpendicular", "shear_perpendicular"} and self.load_duration in _DURATION_CROSS_FIBER else 1.0
        m_sm = 1.15 if stress == "compression_perpendicular" and self.load_duration in _DURATION_COMPRESSION_PERPENDICULAR else 1.0
        return {
            "m_v": self.service_class_factor,
            "m_dlt": self.duration_factor,
            "m_dlt_cross_fiber": cross_fiber,
            "m_sm": m_sm,
            "m_t": self.temperature_factor,
            "m_service_life": self.m_service_life(stress),
        }

    def multiplier(self, stress: str) -> float:
        factors = self.factors(stress)
        return factors["m_v"] * factors["m_dlt"] * factors["m_dlt_cross_fiber"] * factors["m_sm"] * factors["m_t"] * factors["m_service_life"]

    def elastic_multiplier(self) -> float:
        return self.service_class_factor * self.elastic_duration_factor * self.temperature_factor * self.m_service_life("bending")

    def validate_environment(self, wood_moisture_pct: float, relative_humidity_pct: float) -> None:
        if self.service_class == "4б":
            if wood_moisture_pct <= 20:
                raise ValueError("Для класса 4б влажность древесины должна быть более 20 %")
            if relative_humidity_pct <= 85:
                raise ValueError("Для класса 4б влажность воздуха должна быть более 85 %")
        elif self.service_class == "4а":
            if wood_moisture_pct <= 20 and relative_humidity_pct <= 85:
                raise ValueError("Для класса 4а должно выполняться хотя бы одно условие: более 20 % или более 85 %")

    def to_dict(self) -> dict[str, Any]:
        return {
            "load_duration": self.load_duration,
            "service_class": self.service_class,
            "service_class_display": self.service_class_display,
            "temperature_c": self.temperature_c,
            "service_life_years": self.service_life_years,
            "temperature_factor": self.temperature_factor,
        }


class _Material:
    source_revision: ClassVar[str] = SOURCE_REVISION
    source_tables: ClassVar[tuple[str, ...]] = ()
    material_type: ClassVar[str] = "wood material"

    context: WoodContext | None
    _normative: Mapping[str, float | None]
    _design_base: Mapping[str, float | None]

    E_mean_MPa: float | None = None
    E_05_MPa: float | None = None
    E_perp_mean_MPa: float | None = None
    G_mean_MPa: float | None = None
    density_mean_kg_m3: float | None = None
    density_k_kg_m3: float | None = None
    density_for_weight_kg_m3: float | None = None

    def _base_resistance(self, stress: str, design: bool) -> float:
        stress = _canonical_stress(stress)
        mapping = self._design_base if design else self._normative
        value = mapping.get(stress)
        if value is None:
            raise ValueError(f"Для материала {self} отсутствует нормативное значение: {stress}")
        return float(value)

    def _factor_resistance(self, stress: str, base: float, design: bool) -> float:
        if not design:
            return base
        if self.context is None:
            raise ValueError("Для расчётного сопротивления нужен явный режим нагружения")
        return base * self.context.multiplier(stress)

    def resistance(self, stress: str, design: bool = True) -> float:
        return self._factor_resistance(stress, self._base_resistance(stress, design), design)

    def factors(self, stress: str = "bending") -> dict[str, float]:
        if self.context is None:
            return {}
        return self.context.factors(stress)

    @property
    def E_II_MPa(self) -> float | None:
        if self.E_mean_MPa is None or self.context is None:
            return None
        return self.E_mean_MPa * self.context.elastic_multiplier()

    def _parameters(self) -> dict[str, Any]:
        return {}

    def to_dict(self) -> dict[str, Any]:
        resistances: dict[str, float | None] = {}
        if self.context is not None:
            for stress in STRESS_NAMES:
                try:
                    resistances[stress] = self.resistance(stress)
                except ValueError:
                    resistances[stress] = None
        return {
            "material_type": self.material_type,
            "source_revision": self.source_revision,
            "source_tables": list(self.source_tables),
            "parameters": self._parameters(),
            "context": self.context.to_dict() if self.context else None,
            "base_resistances_MPa": dict(self._normative),
            "resistances_MPa": resistances,
            "factors": self.factors("bending"),
            "factors_by_stress": {stress: self.factors(stress) for stress in STRESS_NAMES} if self.context else {},
            "E_mean_MPa": self.E_mean_MPa,
            "E_05_MPa": self.E_05_MPa,
            "E_perp_mean_MPa": self.E_perp_mean_MPa,
            "G_mean_MPa": self.G_mean_MPa,
            "E_II_MPa": self.E_II_MPa,
            "density_mean_kg_m3": self.density_mean_kg_m3,
            "density_k_kg_m3": self.density_k_kg_m3,
            "density_for_weight_kg_m3": self.density_for_weight_kg_m3,
        }

    def to_markdown(self) -> str:
        data = self.to_dict()
        rows = [
            f"# {self}",
            "",
            f"Источник: {self.source_revision}",
            "",
            f"Таблицы: {', '.join(self.source_tables)}",
            "",
            "| Параметр | Значение |",
            "|---|---:|",
        ]
        if self.context is not None:
            rows.append(f"Контекст: режим {self.context.load_duration}, класс {self.context.service_class}, температура {self.context.temperature_c:g} °C, срок {self.context.service_life_years:g} лет")
            rows.append("")
        for key in ("E_mean_MPa", "E_05_MPa", "E_perp_mean_MPa", "G_mean_MPa", "E_II_MPa", "density_mean_kg_m3", "density_for_weight_kg_m3"):
            rows.append(f"| {key} | {data[key]} |")
        rows.extend(["", "| Сопротивление | МПа |", "|---|---:|"])
        for stress, value in data["resistances_MPa"].items():
            rows.append(f"| {_STRESS_DISPLAY[stress]} | {value} |")
        return "\n".join(rows)

    def to_html(self) -> str:
        data = self.to_dict()
        context_text = ""
        if self.context is not None:
            context_text = f"<p>Режим {escape(self.context.load_duration)}, класс {escape(self.context.service_class)}, температура {self.context.temperature_c:g} °C, срок {self.context.service_life_years:g} лет</p>"
        rows = [f"<h1>{escape(str(self))}</h1>", f"<p>{escape(self.source_revision)}</p>", f"<p>Таблицы: {escape(', '.join(self.source_tables))}</p>", context_text, '<table><thead><tr><th>Параметр</th><th>Значение</th></tr></thead><tbody>']
        for key in ("E_mean_MPa", "E_05_MPa", "E_perp_mean_MPa", "G_mean_MPa", "E_II_MPa"):
            rows.append(f"<tr><td>{escape(key)}</td><td>{escape(str(data[key]))} МПа</td></tr>")
        for stress, value in data["resistances_MPa"].items():
            rows.append(f"<tr><td>{escape(_STRESS_DISPLAY[stress])}</td><td>{escape(str(value))} МПа</td></tr>")
        rows.append("</tbody></table>")
        return "".join(rows)

    def __repr__(self) -> str:
        return str(self)


def _divide_by_gamma(values: Mapping[str, float | None]) -> dict[str, float | None]:
    return {
        stress: None if value is None else value / MATERIAL_GAMMA.get(stress, 1.0)
        for stress, value in values.items()
    }


class Timber(_Material):
    material_type = "sorted timber"
    source_tables = ("таблица 3", "таблица В.1", "таблица Г.1")
    _DESIGN = {
        1: {"bending": 21.0, "tension_parallel": 15.0, "compression_parallel": 21.0, "compression_perpendicular": 2.7, "shear_parallel": 2.7},
        2: {"bending": 19.5, "tension_parallel": 10.5, "compression_parallel": 19.5, "compression_perpendicular": 2.7, "shear_parallel": 2.4},
        3: {"bending": 13.0, "tension_parallel": None, "compression_parallel": 13.0, "compression_perpendicular": 2.7, "shear_parallel": 2.4},
    }
    _NORMATIVE = {
        1: {"bending": 26.0, "tension_parallel": 20.0, "compression_parallel": 25.0, "compression_perpendicular": 3.6, "shear_parallel": 3.6},
        2: {"bending": 24.0, "tension_parallel": 15.0, "compression_parallel": 23.0, "compression_perpendicular": 3.2, "shear_parallel": 3.2},
        3: {"bending": 16.0, "tension_parallel": None, "compression_parallel": 16.0, "compression_perpendicular": 3.2, "shear_parallel": 3.2},
    }
    _SPECIES_FACTOR = {
        "pine": {"bending": 1.0, "tension_parallel": 1.0, "compression_parallel": 1.0, "compression_perpendicular": 1.0, "shear_parallel": 1.0},
        "spruce": {"bending": 1.0, "tension_parallel": 1.0, "compression_parallel": 1.0, "compression_perpendicular": 1.0, "shear_parallel": 1.0},
        "fir": {"bending": 1.0, "tension_parallel": 1.0, "compression_parallel": 1.0, "compression_perpendicular": 1.0, "shear_parallel": 1.0},
        "cedar": {"bending": 1.0, "tension_parallel": 1.0, "compression_parallel": 1.0, "compression_perpendicular": 1.0, "shear_parallel": 1.0},
        "larch_european": {"bending": 1.0, "tension_parallel": 1.0, "compression_parallel": 1.2, "compression_perpendicular": 1.2, "shear_parallel": 1.0},
        "larch_other": {"bending": 1.2, "tension_parallel": 1.2, "compression_parallel": 1.2, "compression_perpendicular": 1.2, "shear_parallel": 1.0},
    }
    def __init__(self, sort: int, species: str = "pine", geometry_case: str | None = None, context: WoodContext | None = None):
        if sort not in self._DESIGN:
            raise ValueError("Сорт древесины должен быть 1, 2 или 3")
        if geometry_case != "rectangular_edge_h_le_500":
            raise ValueError("Поддерживается только геометрический случай: прямоугольное сечение по кромке, h ≤ 500 мм")
        self.sort = sort
        self.species = _canonical_species(species)
        self.geometry_case = geometry_case
        self.context = context
        self._normative = self._with_species(self._NORMATIVE[sort])
        self._design_base = self._with_species(self._DESIGN[sort])
        self.E_mean_MPa = {1: 11000.0, 2: 10000.0, 3: 9000.0}[sort]
        self.E_05_MPa = {1: 7330.0, 2: 6670.0, 3: 6000.0}[sort]
        self.density_mean_kg_m3 = 650.0 if self.species.startswith("larch") else 500.0
        self.density_k_kg_m3 = 450.0 if self.species.startswith("larch") else 350.0
        self.density_for_weight_kg_m3 = 650.0 if self.species.startswith("larch") else 500.0

    def _with_species(self, values: Mapping[str, float | None]) -> dict[str, float | None]:
        factors = self._SPECIES_FACTOR[self.species]
        return {key: None if value is None else value * factors.get(key, 1.0) for key, value in values.items()}

    def _base_resistance(self, stress: str, design: bool) -> float:
        stress = _canonical_stress(stress)
        mapping = self._design_base if design else self._normative
        value = mapping.get(stress)
        if value is None:
            if self.sort == 3 and stress == "tension_parallel":
                raise ValueError("растяжение вдоль волокон: отсутствует значение для сорт 3")
            raise ValueError(f"Для материала {self} отсутствует нормативное значение: {stress}")
        return float(value)

    def _parameters(self) -> dict[str, Any]:
        return {"sort": self.sort, "species": self.species, "geometry_case": self.geometry_case}

    def __str__(self) -> str:
        return f"Timber(sort={self.sort}, species={self.species})"


SPECIES_FACTORS = Timber._SPECIES_FACTOR


class StrengthClassWood(_Material):
    material_type = "strength-class solid wood"
    source_tables = ("таблица В.3", "таблица Г.1")
    _DATA = {
        "C14": (14, 8, 16, 0.4, 2.0, 1.7, 350, 290, 7000, 4700),
        "C16": (16, 10, 17, 0.5, 2.2, 1.8, 370, 310, 8000, 5400),
        "C18": (18, 11, 18, 0.5, 2.2, 2.0, 380, 320, 9000, 6000),
        "C20": (20, 12, 19, 0.5, 2.3, 2.2, 390, 330, 9500, 6400),
        "C22": (22, 13, 20, 0.5, 2.4, 2.4, 410, 340, 10000, 6700),
        "C24": (24, 14, 21, 0.5, 2.5, 2.5, 420, 350, 11000, 7400),
        "C27": (27, 16, 22, 0.6, 2.6, 2.8, 450, 370, 11500, 8000),
        "C30": (30, 18, 24, 0.6, 2.7, 3.0, 460, 380, 12000, 8400),
        "C35": (35, 21, 25, 0.6, 2.8, 3.4, 480, 400, 13000, 8700),
        "C40": (40, 24, 26, 0.6, 2.9, 3.8, 500, 420, 14000, 9400),
        "C45": (45, 27, 29, 0.6, 3.1, 3.8, 440, 440, 15000, 10000),
        "C50": (50, 30, 30, 0.6, 3.2, 3.8, 460, 460, 16000, 10700),
    }
    _E_PERP = (230, 270, 300, 320, 330, 370, 380, 400, 430, 470, 500, 530)
    _G_MEAN = (440, 500, 560, 590, 630, 690, 720, 750, 810, 880, 940, 1000)

    def __init__(self, strength_class: str, context: WoodContext | None = None):
        if strength_class not in self._DATA:
            raise ValueError(f"Не поддерживается класс {strength_class}")
        self.strength_class = strength_class
        self.context = context
        bending, tension, compression, tension_perp, compression_perp, shear, density_mean, density_k, e_mean, e05 = self._DATA[strength_class]
        self._normative = {"bending": bending, "tension_parallel": tension, "compression_parallel": compression, "tension_perpendicular": tension_perp, "compression_perpendicular": compression_perp, "shear_parallel": shear, "shear_perpendicular": shear}
        self._design_base = _divide_by_gamma(self._normative)
        self.E_mean_MPa = float(e_mean)
        self.E_05_MPa = float(e05)
        index = list(self._DATA).index(strength_class)
        self.E_perp_mean_MPa = float(self._E_PERP[index])
        self.G_mean_MPa = float(self._G_MEAN[index])
        self.density_mean_kg_m3 = float(density_mean)
        self.density_k_kg_m3 = float(density_k)
        self.density_for_weight_kg_m3 = float(density_mean)

    def _parameters(self) -> dict[str, Any]:
        return {"strength_class": self.strength_class}

    def __str__(self) -> str:
        return f"StrengthClassWood({self.strength_class})"


class Glulam(_Material):
    material_type = "glued laminated timber"
    source_tables = ("таблица В.4", "таблица Г.1")
    _DATA = {
        "K20": (20, 14, 20, 2.5, 3.5, 430, 360, 10500, 8500),
        "K24": (24, 16, 24, 2.7, 3.8, 450, 380, 11500, 9400),
        "K28": (28, 19, 26, 3.0, 4.0, 470, 390, 12500, 10200),
        "K32": (32, 22, 29, 3.4, 4.2, 490, 410, 13500, 11000),
        "K36": (36, 25, 31, 3.8, 4.5, 510, 430, 14500, 11800),
    }

    def __init__(self, glulam_class: str, context: WoodContext | None = None):
        if glulam_class not in self._DATA:
            raise ValueError(f"Не поддерживается класс {glulam_class}")
        self.glulam_class = glulam_class
        self.context = context
        bending, tension, compression, tension_perp, shear, density_mean, density_k, e_mean, e05 = self._DATA[glulam_class]
        self._normative = {"bending": bending, "tension_parallel": tension, "compression_parallel": compression, "tension_perpendicular": tension_perp, "compression_perpendicular": compression * 0.13, "shear_parallel": shear, "shear_perpendicular": shear}
        self._design_base = _divide_by_gamma(self._normative)
        self.E_mean_MPa = float(e_mean)
        self.E_05_MPa = float(e05)
        self.E_perp_mean_MPa = 300.0
        self.G_mean_MPa = 650.0
        self.density_mean_kg_m3 = float(density_mean)
        self.density_k_kg_m3 = float(density_k)
        self.density_for_weight_kg_m3 = float(density_mean)

    def _parameters(self) -> dict[str, Any]:
        return {"glulam_class": self.glulam_class}

    def __str__(self) -> str:
        return f"Glulam({self.glulam_class})"


class LVL(_Material):
    material_type = "laminated veneer lumber"
    source_tables = ("таблица В.2", "таблица В.2а", "таблица В.7", "таблица Г.1")
    _DATA = {
        "1/K45": (45, 31, 41, 1.7, 4.1, 5100, 12000, 550),
        "2/K40": (40, 28, 36, 1.7, 4.0, 5000, 11000, 550),
        "3/K35": (35, 24, 32, 1.6, 3.8, 4800, 10000, 550),
    }

    def __init__(self, lvl_class: str, context: WoodContext | None = None):
        if lvl_class not in self._DATA:
            raise ValueError(f"Не поддерживается класс LVL {lvl_class}")
        self.lvl_class = lvl_class
        self.context = context
        bending, tension, compression, tension_perp, shear, e05, e_mean, density = self._DATA[lvl_class]
        self._normative = {"bending": bending, "tension_parallel": tension, "compression_parallel": compression, "tension_perpendicular": tension_perp, "compression_perpendicular": 3.0, "shear_parallel": shear}
        self._design_base = {
            "bending": 39.0,
            "tension_parallel": 31.0,
            "compression_parallel": 36.0,
            "tension_perpendicular": 1.5,
            "compression_perpendicular": 3.0,
            "shear_parallel": 3.5,
        }
        self.E_mean_MPa = float(e_mean)
        self.E_05_MPa = None
        self.E_perp_mean_MPa = 300.0
        self.G_mean_MPa = 650.0
        self.density_mean_kg_m3 = float(density)
        self.density_k_kg_m3 = None
        self.density_for_weight_kg_m3 = float(density)

    def _parameters(self) -> dict[str, Any]:
        return {"lvl_class": self.lvl_class}

    def __str__(self) -> str:
        return f"LVL({self.lvl_class})"


class Plywood(_Material):
    material_type = "plywood"
    source_tables = ("таблица В.5", "таблица В.6", "таблица Г.1")

    def __init__(self, kind: str, thickness_mm: float, layers: int, direction: str = "parallel", context: WoodContext | None = None):
        if kind not in {"FSF_birch", "FBS"}:
            raise ValueError("Поддерживаются только фанера FSF_birch и ФБС")
        if layers < 3 or layers % 2 == 0:
            raise ValueError("Число слоёв фанеры должно быть нечётным и не менее 3")
        if thickness_mm < 8 and layers == 7:
            raise ValueError("Для 7-слойной фанеры требуется номинальная толщина не менее 7-слойного диапазона")
        if direction not in {"parallel", "perpendicular"}:
            raise ValueError("Направление фанеры должно быть parallel или perpendicular")
        self.kind = kind
        self.thickness_mm = float(thickness_mm)
        self.layers = int(layers)
        self.direction = direction
        self.context = context
        parallel = {"bending": 24.0, "tension_parallel": 18.0, "compression_parallel": 20.0, "tension_perpendicular": 1.2, "compression_perpendicular": 9.0, "shear_parallel": 2.0}
        perpendicular = {"bending": 12.0, "tension_parallel": 10.0, "compression_parallel": 12.0, "tension_perpendicular": 1.2, "compression_perpendicular": 7.5, "shear_parallel": 1.2}
        if kind == "FBS":
            parallel = {"bending": 48.5, "tension_parallel": 42.5, "compression_parallel": 50.0, "tension_perpendicular": 2.7, "compression_perpendicular": 16.5, "shear_parallel": 16.5}
            perpendicular = {"bending": 36.5, "tension_parallel": 35.0, "compression_parallel": 38.0, "tension_perpendicular": 2.7, "compression_perpendicular": 18.0, "shear_parallel": 18.0}
        self._design_base = dict(parallel if direction == "parallel" else perpendicular)
        self._normative = dict(self._design_base)
        self.E_mean_MPa = (12000.0 if kind == "FBS" else 9000.0) if direction == "parallel" else (6000.0 if kind == "FBS" else 4500.0)
        self.E_05_MPa = None
        self.E_perp_mean_MPa = 600.0
        self.G_mean_MPa = 1000.0 if kind == "FBS" else 750.0
        self.density_mean_kg_m3 = 1000.0 if kind == "FBS" else 700.0
        self.density_k_kg_m3 = None
        self.density_for_weight_kg_m3 = self.density_mean_kg_m3

    def _base_resistance(self, stress: str, design: bool) -> float:
        if not design:
            raise ValueError("Для фанеры нормативные значения без расчётной схемы не определены")
        return super()._base_resistance(stress, design)

    def _parameters(self) -> dict[str, Any]:
        return {"kind": self.kind, "thickness_mm": self.thickness_mm, "layers": self.layers, "direction": self.direction}

    def __str__(self) -> str:
        return f"Plywood({self.kind}, {self.thickness_mm:g} mm, {self.layers}-слойная, {self.direction})"


class OSB3(_Material):
    material_type = "OSB/3"
    source_tables = ("таблица В.6", "таблица Г.1")

    def __init__(self, direction: str = "major", context: WoodContext | None = None):
        if direction not in {"major", "minor"}:
            raise ValueError("направление OSB/3 должно быть major или minor")
        self.direction = direction
        self.context = context
        if direction == "major":
            self._design_base = {"bending": 23.0, "tension_parallel": 18.0, "compression_parallel": 20.0, "shear_parallel": 2.5}
            self.E_mean_MPa = 3600.0
        else:
            self._design_base = {"bending": 11.0, "tension_parallel": 9.0, "compression_parallel": 10.0, "shear_parallel": 1.5}
            self.E_mean_MPa = 1400.0
        self._normative = dict(self._design_base)
        self.E_05_MPa = None
        self.E_perp_mean_MPa = 1400.0 if direction == "major" else 3600.0
        self.G_mean_MPa = 1100.0
        self.density_mean_kg_m3 = 600.0
        self.density_k_kg_m3 = None
        self.density_for_weight_kg_m3 = 600.0

    def _base_resistance(self, stress: str, design: bool) -> float:
        if not design:
            raise ValueError("Для OSB нормативные значения без расчётной схемы не определены")
        return super()._base_resistance(stress, design)

    def _parameters(self) -> dict[str, Any]:
        return {"direction": self.direction}

    def __str__(self) -> str:
        return f"OSB3({self.direction})"


def list_strength_classes() -> list[str]:
    return list(StrengthClassWood._DATA)


def list_glulam_classes() -> list[str]:
    return list(Glulam._DATA)


def list_lvl_classes() -> list[str]:
    return list(LVL._DATA)


def list_service_classes() -> list[str]:
    return list(SERVICE_CLASSES)


def list_load_duration_modes() -> list[str]:
    return list(LOAD_DURATION_MODES)


def list_wood_species() -> list[str]:
    return list(_SPECIES)


def generate_wood_code_snippet(material: _Material) -> str:
    """Сгенерировать самодостаточный фрагмент Python с переменной ``material``."""
    if not isinstance(material, _Material):
        raise TypeError("Ожидался материал из sp64_materials")
    parameters = material._parameters()
    class_name = type(material).__name__
    args = ", ".join(f"{key}={value!r}" for key, value in parameters.items())
    if material.context is not None:
        context = material.context
        context_code = (
            f"WoodContext(load_duration={context.load_duration!r}, service_class={context.service_class!r}, "
            f"temperature_c={context.temperature_c!r}, service_life_years={context.service_life_years!r})"
        )
        args = f"{args}, context={context_code}"
    return f"from sp64_materials import {class_name}, WoodContext\n\nmaterial = {class_name}({args})\n"


__all__ = [
    "Glulam",
    "LVL",
    "MATERIAL_GAMMA",
    "OSB3",
    "Plywood",
    "SOURCE_REVISION",
    "SPECIES_FACTORS",
    "StrengthClassWood",
    "Timber",
    "WoodContext",
    "generate_wood_code_snippet",
    "list_glulam_classes",
    "list_load_duration_modes",
    "list_lvl_classes",
    "list_service_classes",
    "list_strength_classes",
    "list_wood_species",
]

