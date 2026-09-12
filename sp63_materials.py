"""
sp63_materials.py
-----------------
Модуль для определения нормативных и расчетных характеристик материалов
(бетона и арматуры) и построения деформационных диаграмм по СП 63.13330.2018
"Бетонные и железобетонные конструкции. Основные положения" (с Изменениями № 1).

Разработчик: Antigravity AI Pair Programmer
Дата: 2026-09-12
"""

from typing import Dict, Tuple, List, Optional, Union
import numpy as np


# ==============================================================================
# НОРМАТИВНЫЕ ТАБЛИЦЫ СП 63.13330.2018
# ==============================================================================

# Классы бетона по прочности на сжатие (п. 6.1.4)
CONCRETE_GRADES = [
    'B1.5', 'B2', 'B2.5', 'B3.5', 'B5', 'B7.5', 'B10', 'B12.5', 'B15', 'B20', 'B25',
    'B30', 'B35', 'B40', 'B45', 'B50', 'B55', 'B60', 'B70',
    'B80', 'B90', 'B100'
]

# Таблица 6.7: Нормативные сопротивления бетона Rbn, Rbtn, МПа
# (и расчетные для предельных состояний II группы: Rb,ser = Rbn, Rbt,ser = Rbtn)
# Для тяжелого, мелкозернистого и напрягающего бетонов
TABLE_6_7_RBN = {
    'B3.5': 2.7, 'B5': 3.5, 'B7.5': 5.5, 'B10': 7.5, 'B12.5': 9.5,
    'B15': 11.0, 'B20': 15.0, 'B25': 18.5, 'B30': 22.0, 'B35': 25.5,
    'B40': 29.0, 'B45': 32.0, 'B50': 36.0, 'B55': 39.5, 'B60': 43.0,
    'B70': 50.0, 'B80': 57.0, 'B90': 64.0, 'B100': 71.0
}

TABLE_6_7_RBTN = {
    'B3.5': 0.39, 'B5': 0.55, 'B7.5': 0.70, 'B10': 0.85, 'B12.5': 1.00,
    'B15': 1.10, 'B20': 1.35, 'B25': 1.55, 'B30': 1.75, 'B35': 1.95,
    'B40': 2.10, 'B45': 2.25, 'B50': 2.45, 'B55': 2.60, 'B60': 2.75,
    'B70': 3.00, 'B80': 3.30, 'B90': 3.60, 'B100': 3.80
}

# Таблица 6.8: Расчетные сопротивления бетона Rb, Rbt, МПа (I группа ПС)
# Для тяжелого, мелкозернистого и напрягающего бетонов
TABLE_6_8_RB = {
    'B3.5': 2.1, 'B5': 2.8, 'B7.5': 4.5, 'B10': 6.0, 'B12.5': 7.5,
    'B15': 8.5, 'B20': 11.5, 'B25': 14.5, 'B30': 17.0, 'B35': 19.5,
    'B40': 22.0, 'B45': 25.0, 'B50': 27.5, 'B55': 30.0, 'B60': 33.0,
    'B70': 37.0, 'B80': 41.0, 'B90': 44.0, 'B100': 47.5
}

TABLE_6_8_RBT = {
    'B3.5': 0.26, 'B5': 0.37, 'B7.5': 0.48, 'B10': 0.56, 'B12.5': 0.66,
    'B15': 0.75, 'B20': 0.90, 'B25': 1.05, 'B30': 1.15, 'B35': 1.30,
    'B40': 1.40, 'B45': 1.50, 'B50': 1.60, 'B55': 1.70, 'B60': 1.80,
    'B70': 1.90, 'B80': 2.10, 'B90': 2.15, 'B100': 2.20
}

# Таблица 6.11: Начальный модуль упругости бетона Eb, МПа * 10^-3 (для тяжелого бетона)
TABLE_6_11_EB = {
    'B3.5': 9.5, 'B5': 13.0, 'B7.5': 16.0, 'B10': 19.0, 'B12.5': 21.5,
    'B15': 24.0, 'B20': 27.5, 'B25': 30.0, 'B30': 32.5, 'B35': 34.5,
    'B40': 36.0, 'B45': 37.0, 'B50': 38.0, 'B55': 39.0, 'B60': 39.5,
    'B70': 41.0, 'B80': 42.0, 'B90': 42.5, 'B100': 43.0
}

# Таблица 6.12: Коэффициент ползучести бетона phi_b_cr
# Влажность: '>75%', '40-75%', '<40%'
TABLE_6_12_PHI_CR = {
    '>75%': {
        'B10': 2.8, 'B15': 2.4, 'B20': 2.0, 'B25': 1.8, 'B30': 1.6,
        'B35': 1.5, 'B40': 1.4, 'B45': 1.3, 'B50': 1.2, 'B55': 1.1,
        'B60': 1.0, 'B70': 1.0, 'B80': 1.0, 'B90': 1.0, 'B100': 1.0
    },
    '40-75%': {
        'B10': 3.9, 'B15': 3.4, 'B20': 2.8, 'B25': 2.5, 'B30': 2.3,
        'B35': 2.1, 'B40': 1.9, 'B45': 1.8, 'B50': 1.6, 'B55': 1.5,
        'B60': 1.4, 'B70': 1.4, 'B80': 1.4, 'B90': 1.4, 'B100': 1.4
    },
    '<40%': {
        'B10': 5.6, 'B15': 4.8, 'B20': 4.0, 'B25': 3.6, 'B30': 3.2,
        'B35': 3.0, 'B40': 2.8, 'B45': 2.6, 'B50': 2.4, 'B55': 2.2,
        'B60': 2.0, 'B70': 2.0, 'B80': 2.0, 'B90': 2.0, 'B100': 2.0
    }
}

# Таблица 6.10: Относительные деформации бетона при продолжительном действии нагрузки
TABLE_6_10_DEFORMATIONS = {
    '>75%': {
        'eps_b0': 0.0030, 'eps_b2': 0.0042, 'eps_b1_red': 0.0024,
        'eps_bt0': 0.00021, 'eps_bt2': 0.00027, 'eps_bt1_red': 0.00019,
    },
    '40-75%': {
        'eps_b0': 0.0034, 'eps_b2': 0.0048, 'eps_b1_red': 0.0028,
        'eps_bt0': 0.00024, 'eps_bt2': 0.00031, 'eps_bt1_red': 0.00022,
    },
    '<40%': {
        'eps_b0': 0.0040, 'eps_b2': 0.0056, 'eps_b1_red': 0.0034,
        'eps_bt0': 0.00028, 'eps_bt2': 0.00036, 'eps_bt1_red': 0.00026,
    },
}

# Таблица 6.13: Нормативные сопротивления арматуры Rsn, МПа (и II группа ПС: Rs,ser = Rsn)
TABLE_6_13_RSN = {
    'A240': 240.0,
    'A400': 390.0,
    'A500': 500.0,
    'A600': 600.0,
    'A800': 800.0,
    'A1000': 1000.0,
    'B500': 500.0,
    'Bp500': 500.0,
    'Bp1200': 1200.0,
    'Bp1300': 1300.0,
    'Bp1400': 1400.0,
    'Bp1500': 1500.0,
    'Bp1600': 1600.0,
    'K1400': 1400.0,
    'K1450': 1450.0,
    'K1500': 1500.0,
    'K1550': 1550.0,
    'K1650': 1650.0,
    'K1750': 1740.0,
    'K1850': 1840.0,
    'K1900': 1920.0,
}

# Таблица 6.14: Расчетные сопротивления арматуры Rs, Rsc, МПа (I группа ПС)
# Rsc_short - при кратковременном действии (в скобках в табл. 6.14)
# Rsc_long  - при длительном действии
TABLE_6_14_REBAR = {
    'A240':  {'Rs': 210.0, 'Rsc_short': 210.0, 'Rsc_long': 210.0},
    'A400':  {'Rs': 340.0, 'Rsc_short': 340.0, 'Rsc_long': 340.0},
    'A500':  {'Rs': 435.0, 'Rsc_short': 400.0, 'Rsc_long': 435.0},
    'A600':  {'Rs': 520.0, 'Rsc_short': 400.0, 'Rsc_long': 470.0},
    'A800':  {'Rs': 695.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'A1000': {'Rs': 870.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'B500':  {'Rs': 415.0, 'Rsc_short': 380.0, 'Rsc_long': 415.0},
    'Bp500': {'Rs': 415.0, 'Rsc_short': 360.0, 'Rsc_long': 390.0},
    'Bp1200': {'Rs': 1000.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'Bp1300': {'Rs': 1100.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'Bp1400': {'Rs': 1170.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'Bp1500': {'Rs': 1250.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'Bp1600': {'Rs': 1340.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'K1400': {'Rs': 1170.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'K1450': {'Rs': 1200.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'K1500': {'Rs': 1250.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'K1550': {'Rs': 1350.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'K1650': {'Rs': 1435.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'K1750': {'Rs': 1515.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'K1850': {'Rs': 1600.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'K1900': {'Rs': 1670.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
}

# Таблица 6.15: Поперечная арматура Rsw, МПа
TABLE_6_15_RSW = {
    'A240': 170.0,
    'A400': 280.0,
    'A500': 300.0,
    'B500': 300.0,
}

# Rows of tables 6.7 and 6.8 that are not applicable to heavy concrete.  The
# main tables above deliberately remain the heavy/fine-grained/tensioning
# profile; these small catalogs prevent a light or cellular grade from being
# silently substituted with a heavy-concrete row.
TABLE_6_7_LIGHT_RBN = {
    'B2.5': 1.9, 'B3.5': 2.7, 'B5': 3.5, 'B7.5': 5.5, 'B10': 7.5,
    'B12.5': 9.5, 'B15': 11.0, 'B20': 15.0, 'B25': 18.5, 'B30': 22.0,
    'B35': 25.5, 'B40': 29.0,
}
TABLE_6_7_LIGHT_RBTN = {
    'B2.5': 0.31, 'B3.5': 0.39, 'B5': 0.55, 'B7.5': 0.70, 'B10': 0.85,
    'B12.5': 1.00, 'B15': 1.10, 'B20': 1.35, 'B25': 1.55, 'B30': 1.75,
    'B35': 1.95, 'B40': 2.10,
}
TABLE_6_7_CELLULAR_RBN = {
    'B1.5': 0.95, 'B2': 1.3, 'B2.5': 1.6, 'B3.5': 2.2, 'B5': 3.1,
    'B7.5': 4.6, 'B10': 6.0, 'B12.5': 7.0, 'B15': 7.7,
}
TABLE_6_7_CELLULAR_RBTN = {
    'B1.5': 0.09, 'B2': 0.12, 'B2.5': 0.14, 'B3.5': 0.18, 'B5': 0.24,
    'B7.5': 0.28, 'B10': 0.39, 'B12.5': 0.44, 'B15': 0.46,
}

CONCRETE_TYPE_ALIASES = {
    'heavy': 'heavy', 'тяжелый': 'heavy', 'тяжёлый': 'heavy',
    'fine_grained': 'fine_grained', 'fine-grained': 'fine_grained',
    'мелкозернистый': 'fine_grained',
    'tensioning': 'tensioning', 'напрягающий': 'tensioning',
    'light': 'light', 'легкий': 'light', 'лёгкий': 'light',
    'porous': 'porous', 'поризованный': 'porous',
    'cellular': 'cellular', 'ячеистый': 'cellular',
}


# ==============================================================================
# КЛАСС БЕТОНА
# ==============================================================================

class Concrete:
    """
    Класс характеристик бетона по СП 63.13330.2018.

    Параметры
    ---------
    grade : str
        Класс бетона по прочности на сжатие (например 'B25', 'B30').
    concrete_type : str
        Вид бетона: 'heavy' (тяжелый), 'fine_grained' (мелкозернистый).
    humidity : str
        Относительная влажность воздуха окружающей среды:
        '<40%', '40-75%', '>75%' (по умолчанию '40-75%').
    long_term : bool
        True, если учитывается длительное действие нагрузки (по умолчанию True).
    gamma_b1 : Optional[float]
        Коэффициент условий работы бетона (п. 6.1.12 а):
        0.90 при длительном действии нагрузки, 1.00 при кратковременном.
        Если None, определяется автоматически по флагу long_term.
    gamma_b2 : float
        Коэффициент условий работы бетона (п. 6.1.12 б, по умолчанию 1.0).
    gamma_b3 : float
        Коэффициент условий работы бетона (п. 6.1.12 в, по умолчанию 1.0;
        0.85 для вертикально бетонируемых конструкций высотой более 1.5 м).
    gamma_b4 : float
        Коэффициент условий работы бетона (п. 6.1.12 г, замораживание, по умолчанию 1.0).
    gamma_b5 : float
        Коэффициент условий работы бетона (п. 6.1.12 д, температура, по умолчанию 1.0).
    """

    def __init__(
        self,
        grade: str = 'B25',
        concrete_type: str = 'heavy',
        humidity: str = '40-75%',
        long_term: bool = True,
        gamma_b1: Optional[float] = None,
        gamma_b2: float = 1.0,
        gamma_b3: float = 1.0,
        gamma_b4: float = 1.0,
        gamma_b5: float = 1.0,
        density: Optional[float] = None,
        curing: Optional[str] = None,
        cellular_humidity_percent: Optional[float] = None,
        is_tensioning: bool = False,
    ):
        grade_clean = grade.strip().upper().replace(',', '.')
        if not grade_clean.startswith('B'):
            grade_clean = 'B' + grade_clean
        concrete_type_clean = CONCRETE_TYPE_ALIASES.get(
            str(concrete_type).strip().lower(), str(concrete_type).strip().lower()
        )
        if concrete_type_clean not in {'heavy', 'fine_grained', 'tensioning', 'light', 'porous', 'cellular'}:
            raise ValueError(f"Неизвестный вид бетона: '{concrete_type}'.")
        if grade_clean not in CONCRETE_GRADES:
            raise ValueError(f"Неизвестный класс бетона: '{grade}'. Доступные: {CONCRETE_GRADES}")
        if concrete_type_clean in {'heavy', 'fine_grained', 'tensioning'} and grade_clean not in TABLE_6_8_RB:
            raise ValueError(f"Класс {grade_clean} отсутствует в таблицах 6.7/6.8 для вида бетона '{concrete_type_clean}'.")
        variant_catalog = {
            'light': TABLE_6_7_LIGHT_RBN,
            'porous': TABLE_6_7_LIGHT_RBN,
            'cellular': TABLE_6_7_CELLULAR_RBN,
        }
        if concrete_type_clean in variant_catalog and grade_clean not in variant_catalog[concrete_type_clean]:
            raise ValueError(f"Класс {grade_clean} отсутствует в таблицах для вида бетона '{concrete_type_clean}'.")
        if concrete_type_clean in {'light', 'porous'} and density is None:
            raise ValueError("Для легкого/поризованного бетона требуется density (плотность).")
        if concrete_type_clean == 'cellular' and (density is None or cellular_humidity_percent is None):
            raise ValueError("Для ячеистого бетона требуются density и cellular_humidity_percent.")
        if density is not None and (not np.isfinite(density) or density <= 0):
            raise ValueError("density должна быть положительной и конечной.")
        if cellular_humidity_percent is not None and not np.isfinite(cellular_humidity_percent):
            raise ValueError("cellular_humidity_percent должна быть конечной.")

        self.grade = grade_clean
        self.concrete_type = concrete_type_clean
        self.density = None if density is None else float(density)
        self.curing = None if curing is None else str(curing).strip().lower()
        self.cellular_humidity_percent = (
            None if cellular_humidity_percent is None else float(cellular_humidity_percent)
        )
        self.is_tensioning = bool(is_tensioning or concrete_type_clean == 'tensioning')
        if humidity not in ['<40%', '40-75%', '>75%']:
            raise ValueError("humidity должен быть одним из: '<40%', '40-75%', '>75%'")
        self.humidity = humidity
        self.long_term = long_term

        # Автоматическое определение gamma_b1 при None.  Для ячеистого и
        # поризованного бетона СП 63 задаёт 0.85 при длительной нагрузке.
        if gamma_b1 is None:
            self.gamma_b1 = (0.85 if concrete_type_clean in {'cellular', 'porous'} else 0.90) if long_term else 1.00
        else:
            self.gamma_b1 = float(gamma_b1)

        self.gamma_b2 = float(gamma_b2)
        self.gamma_b3 = float(gamma_b3)
        self.gamma_b4 = float(gamma_b4)
        self.gamma_b5 = float(gamma_b5)
        for name in ('gamma_b1', 'gamma_b2', 'gamma_b3', 'gamma_b4', 'gamma_b5'):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} должен быть положительным и конечным.")
        if self.gamma_b5 > 1.0:
            raise ValueError("gamma_b5 не может быть больше 1.0.")
        if self.concrete_type == 'cellular' and self.cellular_humidity_percent < 0:
            raise ValueError("cellular_humidity_percent не может быть отрицательной.")

    @property
    def gamma_b_total(self) -> float:
        """Итоговый коэффициент условий работы для осевого сжатия Rb."""
        return self.gamma_b1 * self.gamma_b2 * self.gamma_b3 * self.gamma_b4 * self.gamma_b5

    @property
    def gamma_bt_total(self) -> float:
        """Итоговый коэффициент условий работы для осевого растяжения Rbt (без gamma_b3)."""
        return self.gamma_b1 * self.gamma_b2 * self.gamma_b4 * self.gamma_b5

    # Базовые нормативные и расчетные характеристики
    def _catalog_values(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        if self.concrete_type in {'heavy', 'fine_grained', 'tensioning'}:
            return TABLE_6_7_RBN, TABLE_6_7_RBTN
        if self.concrete_type == 'cellular':
            return TABLE_6_7_CELLULAR_RBN, TABLE_6_7_CELLULAR_RBTN
        return TABLE_6_7_LIGHT_RBN, TABLE_6_7_LIGHT_RBTN

    def _type_factor_rbt(self) -> float:
        if self.concrete_type == 'porous':
            factor = 0.7
        elif self.concrete_type in {'light', 'fine_grained'}:
            factor = 0.8 if self.concrete_type == 'light' else 0.8
        else:
            factor = 1.0
        if self.is_tensioning:
            factor *= 1.2
        return factor

    @property
    def Rbn(self) -> float:
        """Нормативное сопротивление осевому сжатию Rbn, МПа (табл. 6.7)."""
        return self._catalog_values()[0][self.grade]

    @property
    def Rbtn(self) -> float:
        """Нормативное сопротивление осевому растяжению Rbtn, МПа (табл. 6.7)."""
        return self._catalog_values()[1][self.grade]

    @property
    def Rb_ser(self) -> float:
        """Расчетное сопротивление сжатию для II группы ПС Rb,ser, МПа (табл. 6.7)."""
        return self.Rbn

    @property
    def Rbt_ser(self) -> float:
        """Расчетное сопротивление растяжению для II группы ПС Rbt,ser, МПа (табл. 6.7)."""
        return self.Rbtn

    @property
    def Rb_base(self) -> float:
        """Базовое расчетное сопротивление сжатию Rb без коэффициентов gamma_bi, МПа (табл. 6.8)."""
        if self.concrete_type in {'heavy', 'fine_grained', 'tensioning'}:
            return TABLE_6_8_RB[self.grade]
        if self.concrete_type == 'cellular':
            # Table 6.8 values at 10% moisture; higher moisture is applied
            # through gamma_b4 below, as prescribed by 6.1.12(g).
            return self.Rbn * (TABLE_6_8_RB[self.grade] / TABLE_6_7_RBN[self.grade]) if self.grade in TABLE_6_8_RB else self.Rbn
        return self.Rbn * (TABLE_6_8_RB[self.grade] / TABLE_6_7_RBN[self.grade]) if self.grade in TABLE_6_8_RB else self.Rbn

    @property
    def Rbt_base(self) -> float:
        """Базовое расчетное сопротивление растяжению Rbt без коэффициентов gamma_bi, МПа (табл. 6.8)."""
        if self.concrete_type in {'heavy', 'fine_grained', 'tensioning'}:
            base = TABLE_6_8_RBT[self.grade]
        elif self.grade in TABLE_6_8_RBT and self.grade in TABLE_6_7_RBTN:
            base = self.Rbtn * (TABLE_6_8_RBT[self.grade] / TABLE_6_7_RBTN[self.grade])
        else:
            base = self.Rbtn
        return base * self._type_factor_rbt()

    @property
    def Rb(self) -> float:
        """Расчетное сопротивление сжатию Rb с учетом коэффициентов gamma_bi, МПа."""
        return round(self.Rb_base * self.gamma_b_total * self._b4_factor, 6)

    @property
    def Rbt(self) -> float:
        """Расчетное сопротивление растяжению Rbt с учетом коэффициентов gamma_bi, МПа."""
        return round(self.Rbt_base * self.gamma_bt_total, 6)

    @property
    def Eb(self) -> float:
        """Начальный модуль упругости бетона Eb, МПа (табл. 6.11)."""
        if self.grade not in TABLE_6_11_EB:
            raise ValueError(f"Для класса {self.grade} нет начального модуля в таблице 6.11.")
        value = TABLE_6_11_EB[self.grade] * 1000.0
        if self.concrete_type == 'fine_grained' and self.curing in {'heat_treated', 'thermal', 'a'}:
            value *= 0.89
        if self.concrete_type == 'cellular' and self.curing in {'non_autoclaved', 'non-autoclave'}:
            value *= 0.8
        if self.concrete_type == 'light' and self.density is not None:
            value *= max(0.0, self.density / 2200.0) ** 2
        return value

    @property
    def phi_b_cr(self) -> float:
        """Коэффициент ползучести бетона phi_b,cr (табл. 6.12)."""
        if self.concrete_type == 'cellular':
            raise ValueError("Для ячеистого бетона коэффициент ползучести принимается по специальным указаниям.")
        hum_dict = TABLE_6_12_PHI_CR[self.humidity]
        if self.grade not in hum_dict:
            raise ValueError(f"Для класса {self.grade} нет коэффициента ползучести в таблице 6.12.")
        value = hum_dict[self.grade]
        if self.concrete_type == 'light':
            value *= (self.density / 2200.0) ** 2
        return value

    @property
    def Eb_red(self) -> float:
        """
        Приведенный модуль деформации бетона Eb,red, МПа (п. 6.1.15, формула 6.3).
        При длительном действии нагрузки: Eb,red = Eb / (1 + phi_b_cr).
        При кратковременном: Eb,red = Eb.
        """
        if self.long_term:
            return round(self.Eb / (1.0 + self.phi_b_cr), 1)
        return self.Eb

    @property
    def _b4_factor(self) -> float:
        if self.concrete_type != 'cellular':
            return 1.0
        humidity = self.cellular_humidity_percent
        if humidity <= 10.0:
            return 1.0
        if humidity >= 25.0:
            return 0.8
        return 1.0 - (humidity - 10.0) * 0.2 / 15.0

    # Предельные относительные деформации бетона
    @property
    def eps_b0(self) -> float:
        """
        Относительная деформация при достижении максимального напряжения сжатия Rb (п. 6.1.14 / 6.1.20).
        """
        if self.long_term:
            value = TABLE_6_10_DEFORMATIONS[self.humidity]['eps_b0']
        else:
            value = 0.0020
        return value * self.gamma_b5 * self._deformation_factor

    @property
    def eps_b1_red(self) -> float:
        """Относительная деформация на переходе двухлинейной диаграммы."""
        if self.long_term:
            value = TABLE_6_10_DEFORMATIONS[self.humidity]['eps_b1_red']
        else:
            value = 0.0015
        return value * self.gamma_b5 * self._deformation_factor

    @property
    def eps_b2(self) -> float:
        """
        Предельная относительная деформация бетона при осевом сжатии (п. 6.1.14 / 6.1.20).
        """
        if self.long_term:
            value = TABLE_6_10_DEFORMATIONS[self.humidity]['eps_b2']
            grade_num = float(self.grade.replace('B', ''))
            if grade_num >= 70.0:
                value *= (270.0 - grade_num) / 210.0
        else:
            # Кратковременное действие: отдельное правило для B70--B100.
            grade_num = float(self.grade.replace('B', ''))
            if grade_num <= 60:
                value = 0.0035
            else:
                value = 0.0033 - (grade_num - 70.0) / 30.0 * (0.0033 - 0.0028)
        return value * self.gamma_b5 * self._deformation_factor

    @property
    def eps_bt0(self) -> float:
        """Относительная деформация при достижении Rbt при растяжении (п. 6.1.14 / 6.1.22)."""
        if self.long_term:
            value = TABLE_6_10_DEFORMATIONS[self.humidity]['eps_bt0']
        else:
            value = 0.00010
        return value * self.gamma_b5 * self._deformation_factor

    @property
    def eps_bt1_red(self) -> float:
        """Относительная деформация на переходе двухлинейной диаграммы растяжения."""
        if self.long_term:
            value = TABLE_6_10_DEFORMATIONS[self.humidity]['eps_bt1_red']
        else:
            value = 0.00008
        return value * self.gamma_b5 * self._deformation_factor

    @property
    def eps_bt2(self) -> float:
        """Предельная относительная деформация бетона при осевом растяжении (п. 6.1.14 / 6.1.22)."""
        if self.long_term:
            value = TABLE_6_10_DEFORMATIONS[self.humidity]['eps_bt2']
        else:
            value = 0.00015
        # The high-strength note to table 6.10 applies to compression only.
        return value * self.gamma_b5 * self._deformation_factor

    @property
    def _deformation_factor(self) -> float:
        if self.concrete_type == 'light' and self.density is not None:
            return max(0.7, 0.4 + 0.6 * self.density / 2200.0)
        return 1.0

    # --------------------------------------------------------------------------
    # Деформационные диаграммы
    # --------------------------------------------------------------------------

    def get_diagram(
        self,
        model: str = 'bilinear',
        state: str = 'compression',
        n_points: int = 100,
        signed: bool = False,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Построение деформационной диаграммы состояния бетона sigma - eps.

        Параметры
        ---------
        model : str
            'bilinear' (двухлинейная, п. 6.1.21),
            'trilinear' (трехлинейная, п. 6.1.20),
            'nonlinear' (криволинейная по Приложению Г / СП 63).
        state : str
            'compression' (сжатие) или 'tension' (растяжение).
        n_points : int
            Количество точек для дискретизации кривой.

        Возвращает
        ----------
        (eps_arr, sigma_arr) : Tuple[np.ndarray, np.ndarray]
            Массивы относительных деформаций и напряжений (МПа).
        """
        self._validate_diagram_inputs(model, state, n_points)
        points = self.get_diagram_points(model, state, signed=signed)
        model_clean = model.lower()
        ordered = list(points.values())

        if model_clean == 'nonlinear':
            if state.lower() == 'compression':
                peak = points['peak']
                end = points['eta_085']
                n_rise = max(2, int(round(n_points * 0.72)))
                n_desc = max(2, n_points - n_rise + 1)
                rise = self._sample_appendix_g_branch(0.0, 1.0, n_rise, signed)
                desc = self._sample_appendix_g_branch(1.0, 0.85, n_desc, signed, descending=True)
                eps_arr = np.concatenate((rise[0][:-1], desc[0]))
                sigma_arr = np.concatenate((rise[1][:-1], desc[1]))
                eps_arr[-1], sigma_arr[-1] = end
                eps_arr[np.argmin(np.abs(eps_arr - peak[0]))] = peak[0]
                sigma_arr[np.argmin(np.abs(sigma_arr - peak[1]))] = peak[1]
                return eps_arr, sigma_arr
            # The tensile Appendix G diagram terminates at the normative
            # failure strain after the peak; its post-peak branch is a plateau.
            return self._sample_segments(ordered, n_points)

        return self._sample_segments(ordered, n_points)

    def _validate_diagram_inputs(self, model: str, state: str, n_points: int) -> None:
        if not isinstance(n_points, (int, np.integer)) or n_points <= 0:
            raise ValueError("n_points должен быть положительным целым числом.")
        if str(state).lower() not in {'compression', 'tension'}:
            raise ValueError("state должен быть 'compression' или 'tension'.")
        if str(model).lower() not in {'bilinear', 'trilinear', 'nonlinear'}:
            raise ValueError("Неизвестная model диаграммы бетона.")

    @staticmethod
    def _sample_segments(points: List[Tuple[float, float]], n_points: int) -> Tuple[np.ndarray, np.ndarray]:
        if n_points == 1:
            return np.array([points[0][0]]), np.array([points[0][1]])
        lengths = np.array([abs(points[i + 1][0] - points[i][0]) for i in range(len(points) - 1)], dtype=float)
        if not np.any(lengths):
            lengths[:] = 1.0
        intervals = np.maximum(1, np.floor((n_points - 1) * lengths / lengths.sum()).astype(int))
        while intervals.sum() < n_points - 1:
            residual = (n_points - 1) * lengths / lengths.sum() - intervals
            intervals[int(np.argmax(residual))] += 1
        while intervals.sum() > n_points - 1:
            candidates = np.flatnonzero(intervals > 1)
            if not len(candidates):
                break
            residual = intervals - (n_points - 1) * lengths / lengths.sum()
            intervals[candidates[int(np.argmax(residual[candidates]))]] -= 1
        eps_parts, sig_parts = [], []
        for i, n_intervals in enumerate(intervals):
            e0, s0 = points[i]
            e1, s1 = points[i + 1]
            segment_eps = np.linspace(e0, e1, int(n_intervals) + 1)
            segment_sig = np.linspace(s0, s1, int(n_intervals) + 1)
            if i:
                segment_eps, segment_sig = segment_eps[1:], segment_sig[1:]
            eps_parts.append(segment_eps)
            sig_parts.append(segment_sig)
        return np.concatenate(eps_parts), np.concatenate(sig_parts)

    def _appendix_g_parameters(self, state: str) -> Tuple[float, float, float, float]:
        if state == 'compression':
            sigma_hat = self.Rb_ser
            eps_peak = self.eps_b0
            nu_hat = sigma_hat / max(self.Eb * eps_peak, 1e-12)
            omega_1 = 0.15
            nu_0 = 1.0
        else:
            sigma_hat = self.Rbt_ser
            eps_peak = self.eps_bt0
            nu_hat = 0.5
            omega_1 = 0.15
            nu_0 = 1.0
        return sigma_hat, eps_peak, min(max(nu_hat, 1e-6), 1.0), nu_0

    def _appendix_g_point(self, eta: float, state: str, signed: bool, descending: bool = False) -> Tuple[float, float]:
        sigma_abs, _, nu_hat, nu_0 = self._appendix_g_parameters(state)
        omega_1 = 0.15
        omega_2 = 1.0 - omega_1
        root = np.sqrt(max(0.0, 1.0 - omega_1 * eta - omega_2 * eta * eta))
        if descending:
            nu = nu_hat - (nu_0 - nu_hat) * root
            nu = max(abs(nu), 1e-6)
        else:
            nu = nu_hat + (1.0 - nu_hat) * root
        if state == 'compression':
            sigma_hat = -sigma_abs if signed else sigma_abs
        else:
            sigma_hat = sigma_abs
        return eta * sigma_hat / (self.Eb * nu), eta * sigma_hat

    def _sample_appendix_g_branch(
        self, eta_start: float, eta_end: float, n_points: int, signed: bool, descending: bool = False
    ) -> Tuple[np.ndarray, np.ndarray]:
        eta = np.linspace(eta_start, eta_end, n_points)
        values = [self._appendix_g_point(float(value), 'compression', signed, descending) for value in eta]
        return np.array([value[0] for value in values]), np.array([value[1] for value in values])

    def get_diagram_points(self, model: str = 'bilinear', state: str = 'compression', signed: bool = False) -> Dict[str, Tuple[float, float]]:
        self._validate_diagram_inputs(model, state, 2)
        model_clean, state_clean = model.lower(), state.lower()
        is_comp = state_clean == 'compression'
        R = self.Rb if is_comp else self.Rbt
        sign = -1.0 if is_comp and signed else 1.0
        if model_clean == 'bilinear':
            eps_1 = self.eps_b1_red if is_comp else self.eps_bt1_red
            eps_2 = self.eps_b2 if is_comp else self.eps_bt2
            return {
                'origin': (0.0, 0.0),
                'plateau_start': (sign * eps_1, sign * R),
                'plateau_end': (sign * eps_2, sign * R),
            }
        if model_clean == 'trilinear':
            eps_0 = self.eps_b0 if is_comp else self.eps_bt0
            eps_2 = self.eps_b2 if is_comp else self.eps_bt2
            transition = (0.6 * R / self.Eb, 0.6 * R)
            return {
                'origin': (0.0, 0.0),
                'transition': (sign * transition[0], sign * transition[1]),
                'plateau_start': (sign * eps_0, sign * R),
                'plateau_end': (sign * eps_2, sign * R),
            }
        if is_comp:
            peak = self._appendix_g_point(1.0, 'compression', signed)
            eta_085 = self._appendix_g_point(0.85, 'compression', signed, descending=True)
            return {'origin': (0.0, 0.0), 'peak': peak, 'eta_085': eta_085}
        peak = self._appendix_g_point(1.0, 'tension', signed)
        failure = (self.eps_bt2, self.Rbt_ser)
        return {'origin': (0.0, 0.0), 'peak': peak, 'failure': failure}

    def to_dict(self) -> Dict[str, Union[str, float, bool]]:
        """Сводный словарь всех характеристик бетона."""
        return {
            'grade': self.grade,
            'concrete_type': self.concrete_type,
            'humidity': self.humidity,
            'density_kg_m3': self.density,
            'curing': self.curing,
            'cellular_humidity_percent': self.cellular_humidity_percent,
            'is_tensioning': self.is_tensioning,
            'long_term': self.long_term,
            'gamma_b_total': round(self.gamma_b_total, 3),
            'gamma_b1': self.gamma_b1,
            'gamma_b2': self.gamma_b2,
            'gamma_b3': self.gamma_b3,
            'gamma_b4': self.gamma_b4,
            'gamma_b5': self.gamma_b5,
            'Rbn_MPa': self.Rbn,
            'Rbtn_MPa': self.Rbtn,
            'Rb_ser_MPa': self.Rb_ser,
            'Rbt_ser_MPa': self.Rbt_ser,
            'Rb_base_MPa': self.Rb_base,
            'Rbt_base_MPa': self.Rbt_base,
            'Rb_design_MPa': self.Rb,
            'Rbt_design_MPa': self.Rbt,
            'Eb_initial_MPa': self.Eb,
            'phi_b_cr': self.phi_b_cr,
            'Eb_red_MPa': self.Eb_red,
            'eps_b0': self.eps_b0,
            'eps_b1_red': self.eps_b1_red,
            'eps_b2': self.eps_b2,
            'eps_bt0': self.eps_bt0,
            'eps_bt1_red': self.eps_bt1_red,
            'eps_bt2': self.eps_bt2
        }

    def to_markdown(self) -> str:
        """Формирование сводной таблицы в формате Markdown."""
        d = self.to_dict()
        md = f"""### Характеристики бетона класса **{d['grade']}** (СП 63.13330.2018)

| Параметр | Обозначение | Значение | Ед. изм. |
|:---------|:-----------:|:--------:|:--------:|
| Расчетное сопротивление сжатию (I группа ПС) | $R_b$ | **{d['Rb_design_MPa']}** | МПа |
| Расчетное сопротивление растяжению (I группа ПС) | $R_{{bt}}$ | **{d['Rbt_design_MPa']}** | МПа |
| Нормативное сопротивление сжатию (II группа ПС) | $R_{{bn}} / R_{{b,ser}}$ | {d['Rbn_MPa']} | МПа |
| Нормативное сопротивление растяжению (II группа ПС) | $R_{{btn}} / R_{{bt,ser}}$ | {d['Rbtn_MPa']} | МПа |
| Начальный модуль упругости | $E_b$ | {d['Eb_initial_MPa']:,.0f} | МПа |
| Коэффициент ползучести бетона | $\\varphi_{{b,cr}}$ | {d['phi_b_cr']} | - |
| Приведенный модуль деформации | $E_{{b,red}}$ | **{d['Eb_red_MPa']:,.0f}** | МПа |
| Предельная деформация вершины сжатия | $\\varepsilon_{{b0}}$ | {d['eps_b0']} | - |
| Предельная деформация разрушения сжатия | $\\varepsilon_{{b2}}$ | {d['eps_b2']} | - |
| Предельная деформация вершины растяжения | $\\varepsilon_{{bt0}}$ | {d['eps_bt0']} | - |
| Предельная деформация разрушения растяжения | $\\varepsilon_{{bt2}}$ | {d['eps_bt2']} | - |
| Суммарный коэффициент условий работы | $\\gamma_{{b,total}}$ | {d['gamma_b_total']} | - |
"""
        return md

    def to_html(self) -> str:
        """Формирование сводной таблицы характеристик бетона в формате HTML."""
        d = self.to_dict()
        html = f"""<div style="margin-top: 15px; margin-bottom: 25px;">
<h3 style="margin-bottom: 8px;">Характеристики бетона класса <strong>{d['grade']}</strong> <small style="color: #6c757d;">(СП 63.13330.2018)</small></h3>
<ul style="margin-bottom: 12px; line-height: 1.6;">
  <li><strong>Вид бетона:</strong> Тяжелый</li>
  <li><strong>Влажность среды:</strong> {d['humidity']}</li>
  <li><strong>Длительность нагрузки:</strong> {'Длительная (gamma_b1 = 0.90)' if d['long_term'] else 'Кратковременная (gamma_b1 = 1.00)'}</li>
  <li><strong>Суммарный коэффициент условий работы:</strong> &gamma;<sub>b,total</sub> = {d['gamma_b_total']}</li>
</ul>
<table class="table table-bordered table-striped" style="max-width: 850px; font-size: 14px; background: white;">
  <thead>
    <tr style="background-color: #f8f9fa;">
      <th style="text-align: left; width: 48%;">Параметр</th>
      <th style="text-align: center; width: 18%;">Обозначение</th>
      <th style="text-align: center; width: 18%;">Значение</th>
      <th style="text-align: center; width: 16%;">Ед. изм.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Расчетное сопротивление сжатию (I группа ПС)</td><td style="text-align: center;"><i>R<sub>b</sub></i></td><td style="text-align: center;"><strong>{d['Rb_design_MPa']}</strong></td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Расчетное сопротивление растяжению (I группа ПС)</td><td style="text-align: center;"><i>R<sub>bt</sub></i></td><td style="text-align: center;"><strong>{d['Rbt_design_MPa']}</strong></td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Нормативное сопротивление сжатию (II группа ПС)</td><td style="text-align: center;"><i>R<sub>bn</sub> / R<sub>b,ser</sub></i></td><td style="text-align: center;">{d['Rbn_MPa']}</td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Нормативное сопротивление растяжению (II группа ПС)</td><td style="text-align: center;"><i>R<sub>btn</sub> / R<sub>bt,ser</sub></i></td><td style="text-align: center;">{d['Rbtn_MPa']}</td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Начальный модуль упругости</td><td style="text-align: center;"><i>E<sub>b</sub></i></td><td style="text-align: center;">{d['Eb_initial_MPa']:,.0f}</td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Коэффициент ползучести бетона</td><td style="text-align: center;">&phi;<sub>b,cr</sub></td><td style="text-align: center;">{d['phi_b_cr']}</td><td style="text-align: center;">-</td></tr>
    <tr><td>Приведенный модуль деформации</td><td style="text-align: center;"><i>E<sub>b,red</sub></i></td><td style="text-align: center;"><strong>{d['Eb_red_MPa']:,.0f}</strong></td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Предельная деформация вершины сжатия</td><td style="text-align: center;">&epsilon;<sub>b0</sub></td><td style="text-align: center;">{d['eps_b0']}</td><td style="text-align: center;">-</td></tr>
    <tr><td>Предельная деформация разрушения сжатия</td><td style="text-align: center;">&epsilon;<sub>b2</sub></td><td style="text-align: center;">{d['eps_b2']}</td><td style="text-align: center;">-</td></tr>
    <tr><td>Предельная деформация вершины растяжения</td><td style="text-align: center;">&epsilon;<sub>bt0</sub></td><td style="text-align: center;">{d['eps_bt0']}</td><td style="text-align: center;">-</td></tr>
    <tr><td>Предельная деформация разрушения растяжения</td><td style="text-align: center;">&epsilon;<sub>bt2</sub></td><td style="text-align: center;">{d['eps_bt2']}</td><td style="text-align: center;">-</td></tr>
  </tbody>
</table>
</div>"""
        return html


# ==============================================================================
# КЛАСС АРМАТУРЫ
# ==============================================================================

class Rebar:
    """
    Класс характеристик арматуры по СП 63.13330.2018.

    Параметры
    ---------
    grade : str
        Класс арматуры ('A240', 'A400', 'A500', 'A600', 'A800', 'A1000', 'B500', 'Bp500', 'K1400', 'K1500').
    long_term : bool
        True при длительном действии нагрузки (влияет на предел сжатия Rsc, по умолчанию True).
    gamma_s : float
        Коэффициент условий работы арматуры (п. 6.2.8, по умолчанию 1.0).
    """

    def __init__(
        self,
        grade: str = 'A500',
        long_term: bool = True,
        gamma_s: float = 1.0
    ):
        grade_clean = grade.strip().upper().replace('ВР', 'BP')
        # Замена кириллических обозначений и запись Bp в едином виде.
        grade_clean = grade_clean.replace('А', 'A').replace('В', 'B').replace('К', 'K')
        grade_clean = grade_clean.replace('BP', 'Bp')
        if grade_clean not in TABLE_6_14_REBAR:
            raise ValueError(f"Неизвестный класс арматуры: '{grade}'. Доступные: {list(TABLE_6_14_REBAR.keys())}")
        if not np.isfinite(gamma_s) or gamma_s <= 0:
            raise ValueError("gamma_s должен быть положительным и конечным.")

        self.grade = grade_clean
        self.long_term = long_term
        self.gamma_s = float(gamma_s)

    @property
    def Rsn(self) -> float:
        """Нормативное сопротивление арматуры растяжению Rsn, МПа (табл. 6.13)."""
        return TABLE_6_13_RSN[self.grade]

    @property
    def Rs_ser(self) -> float:
        """Расчетное сопротивление растяжению для II группы ПС Rs,ser, МПа (табл. 6.13)."""
        return self.Rsn

    @property
    def Rs_base(self) -> float:
        """Базовое расчетное сопротивление растяжению Rs без коэффициентов, МПа (табл. 6.14)."""
        return TABLE_6_14_REBAR[self.grade]['Rs']

    @property
    def Rs(self) -> float:
        """Расчетное сопротивление растяжению Rs с учетом gamma_s, МПа."""
        return round(self.Rs_base * self.gamma_s, 2)

    @property
    def Rsc(self) -> float:
        """
        Расчетное сопротивление арматуры сжатию Rsc, МПа (табл. 6.14).
        С учетом длительности нагрузки (не более 400 МПа при кратковременном).
        """
        key = 'Rsc_long' if self.long_term else 'Rsc_short'
        return round(TABLE_6_14_REBAR[self.grade][key] * self.gamma_s, 2)

    @property
    def Rsw(self) -> Optional[float]:
        """Расчетное сопротивление поперечной арматуры Rsw, МПа (табл. 6.15)."""
        return TABLE_6_15_RSW.get(self.grade, None)

    @property
    def is_conditional_yield(self) -> bool:
        """Имеет ли класс условный предел текучести (п. 6.2.11)."""
        return self.grade not in {'A240', 'A400', 'A500', 'B500', 'Bp500'}

    @property
    def diagram_kind(self) -> str:
        """Нормативный тип диаграммы: ``bilinear`` или ``trilinear``."""
        if self.grade in {'A240', 'A400', 'A500', 'B500', 'Bp500'}:
            return 'bilinear'
        if self.grade in {
            'A600', 'A800', 'A1000', 'Bp1200', 'Bp1300', 'Bp1400', 'Bp1500',
            'K1400', 'K1500'
        }:
            return 'trilinear'
        raise ValueError(
            f"Для класса {self.grade} отсутствует нормативная привязка диаграммы в 6.2.13; "
            "выберите явную модель только при наличии обоснования."
        )

    @property
    def Es(self) -> float:
        """Модуль упругости арматуры Es, МПа (п. 6.2.12)."""
        if self.grade.startswith('K'):
            return 1.95e5
        return 2.0e5

    @property
    def eps_s0(self) -> float:
        """Относительная деформация условного/физического предела текучести."""
        value = self.Rs / self.Es
        return value + 0.002 if self.is_conditional_yield else value

    @property
    def eps_s2(self) -> float:
        """Предельная относительная деформация арматуры (п. 6.2.14)."""
        return 0.015 if self.is_conditional_yield else 0.025

    # --------------------------------------------------------------------------
    # Деформационная диаграмма арматуры
    # --------------------------------------------------------------------------

    def get_diagram(
        self,
        model: str = 'auto',
        state: str = 'tension',
        n_points: int = 100,
        signed: bool = False,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Построение деформационной диаграммы состояния арматуры sigma_s - eps_s (п. 6.2.14).

        Параметры
        ---------
        model : str
            'prandtl' / 'bilinear' (двухлинейная диаграмма Прандтля).
        state : str
            'tension' (растяжение, предел Rs) или 'compression' (сжатие, предел Rsc).
        n_points : int
            Количество точек дискретизации.
        """
        self._validate_diagram_inputs(model, state, n_points)
        points = self.get_diagram_points(model, state, signed=signed)
        return Concrete._sample_segments(list(points.values()), n_points)

    def _validate_diagram_inputs(self, model: str, state: str, n_points: int) -> None:
        if not isinstance(n_points, (int, np.integer)) or n_points <= 0:
            raise ValueError("n_points должен быть положительным целым числом.")
        if str(state).lower() not in {'tension', 'compression'}:
            raise ValueError("state должен быть 'tension' или 'compression'.")
        if str(model).lower() not in {'auto', 'bilinear', 'trilinear', 'prandtl', 'hardening'}:
            raise ValueError("Неизвестная model диаграммы арматуры.")

    def _resolve_model(self, model: str) -> str:
        model_clean = str(model).lower()
        if model_clean == 'auto':
            return self.diagram_kind
        if model_clean == 'prandtl':
            return 'bilinear'
        if model_clean == 'hardening':
            return 'trilinear'
        return model_clean

    def get_diagram_points(self, model: str = 'auto', state: str = 'tension', signed: bool = False) -> Dict[str, Tuple[float, float]]:
        self._validate_diagram_inputs(model, state, 2)
        model_clean = self._resolve_model(model)
        is_comp = state.lower() == 'compression'
        resistance = self.Rsc if is_comp else self.Rs
        sign = -1.0 if is_comp and signed else 1.0
        eps_y = self.Rsc / self.Es if is_comp and not self.is_conditional_yield else self.eps_s0
        if model_clean == 'bilinear':
            return {
                'origin': (0.0, 0.0),
                'yield': (sign * eps_y, sign * resistance),
                'plateau_end': (sign * 0.025, sign * resistance),
            }
        if model_clean == 'trilinear':
            eps_s1 = 0.9 * resistance / self.Es
            eps_s0 = resistance / self.Es + (0.002 if self.is_conditional_yield else 0.0)
            eps_s2_limit = 2.0 * eps_s0 - eps_s1
            return {
                'origin': (0.0, 0.0),
                's1': (sign * eps_s1, sign * 0.9 * resistance),
                'yield': (sign * eps_s0, sign * resistance),
                's2_limit': (sign * eps_s2_limit, sign * 1.1 * resistance),
                'plateau_end': (sign * 0.015, sign * 1.1 * resistance),
            }
        raise ValueError("Нормативная модель диаграммы арматуры не определена.")

    def to_dict(self) -> Dict[str, Union[str, float, bool]]:
        """Сводный словарь характеристик арматуры."""
        return {
            'grade': self.grade,
            'long_term': self.long_term,
            'gamma_s': self.gamma_s,
            'Rsn_MPa': self.Rsn,
            'Rs_ser_MPa': self.Rs_ser,
            'Rs_base_MPa': self.Rs_base,
            'Rs_design_MPa': self.Rs,
            'Rsc_design_MPa': self.Rsc,
            'Rsw_MPa': self.Rsw,
            'Es_MPa': self.Es,
            'diagram_kind': self.diagram_kind if self.grade in {
                'A240', 'A400', 'A500', 'A600', 'A800', 'A1000', 'B500', 'Bp500',
                'Bp1200', 'Bp1300', 'Bp1400', 'Bp1500', 'K1400', 'K1500'
            } else None,
            'is_conditional_yield': self.is_conditional_yield,
            'eps_s0': self.eps_s0,
            'eps_s2': self.eps_s2
        }

    def to_markdown(self) -> str:
        """Формирование сводной таблицы характеристик в формате Markdown."""
        d = self.to_dict()
        rsw_str = str(d['Rsw_MPa']) if d['Rsw_MPa'] is not None else "Не применяется"
        md = f"""### Характеристики арматуры класса **{d['grade']}** (СП 63.13330.2018)

| Параметр | Обозначение | Значение | Ед. изм. |
|:---------|:-----------:|:--------:|:--------:|
| Расчетное сопротивление растяжению (I группа ПС) | $R_s$ | **{d['Rs_design_MPa']}** | МПа |
| Расчетное сопротивление сжатию (I группа ПС) | $R_{{sc}}$ | **{d['Rsc_design_MPa']}** | МПа |
| Расчетное сопротивление поперечной арматуры | $R_{{sw}}$ | {rsw_str} | МПа |
| Нормативное сопротивление растяжению (II группа ПС) | $R_{{sn}} / R_{{s,ser}}$ | {d['Rsn_MPa']} | МПа |
| Модуль упругости | $E_s$ | {d['Es_MPa']:,.0f} | МПа |
| Деформация предела текучести | $\\varepsilon_{{s0}}$ | {d['eps_s0']} | - |
| Предельная деформация удлинения | $\\varepsilon_{{s2}}$ | {d['eps_s2']} | - |
| Коэффициент условий работы | $\\gamma_s$ | {d['gamma_s']} | - |
"""
        return md

    def to_html(self) -> str:
        """Формирование сводной таблицы характеристик арматуры в формате HTML."""
        d = self.to_dict()
        rsw_str = f"{d['Rsw_MPa']}" if d['Rsw_MPa'] is not None else "Не применяется"
        rsw_unit = "МПа" if d['Rsw_MPa'] is not None else "-"
        html = f"""<div style="margin-top: 15px; margin-bottom: 25px;">
<h3 style="margin-bottom: 8px;">Характеристики арматуры класса <strong>{d['grade']}</strong> <small style="color: #6c757d;">(СП 63.13330.2018)</small></h3>
<table class="table table-bordered table-striped" style="max-width: 850px; font-size: 14px; background: white;">
  <thead>
    <tr style="background-color: #f8f9fa;">
      <th style="text-align: left; width: 48%;">Параметр</th>
      <th style="text-align: center; width: 18%;">Обозначение</th>
      <th style="text-align: center; width: 18%;">Значение</th>
      <th style="text-align: center; width: 16%;">Ед. изм.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Расчетное сопротивление растяжению (I группа ПС)</td><td style="text-align: center;"><i>R<sub>s</sub></i></td><td style="text-align: center;"><strong>{d['Rs_design_MPa']}</strong></td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Расчетное сопротивление сжатию (I группа ПС)</td><td style="text-align: center;"><i>R<sub>sc</sub></i></td><td style="text-align: center;"><strong>{d['Rsc_design_MPa']}</strong></td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Расчетное сопротивление поперечной арматуры</td><td style="text-align: center;"><i>R<sub>sw</sub></i></td><td style="text-align: center;">{rsw_str}</td><td style="text-align: center;">{rsw_unit}</td></tr>
    <tr><td>Нормативное сопротивление растяжению (II группа ПС)</td><td style="text-align: center;"><i>R<sub>sn</sub> / R<sub>s,ser</sub></i></td><td style="text-align: center;">{d['Rsn_MPa']}</td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Модуль упругости</td><td style="text-align: center;"><i>E<sub>s</sub></i></td><td style="text-align: center;">{d['Es_MPa']:,.0f}</td><td style="text-align: center;">МПа</td></tr>
    <tr><td>Деформация предела текучести</td><td style="text-align: center;">&epsilon;<sub>s0</sub></td><td style="text-align: center;">{d['eps_s0']}</td><td style="text-align: center;">-</td></tr>
    <tr><td>Предельная деформация удлинения</td><td style="text-align: center;">&epsilon;<sub>s2</sub></td><td style="text-align: center;">{d['eps_s2']}</td><td style="text-align: center;">-</td></tr>
    <tr><td>Коэффициент условий работы</td><td style="text-align: center;">&gamma;<sub>s</sub></td><td style="text-align: center;">{d['gamma_s']}</td><td style="text-align: center;">-</td></tr>
  </tbody>
</table>
</div>"""
        return html


# ==============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И ГЕНЕРАТОР СНИППЕТОВ
# ==============================================================================

def list_concrete_grades() -> List[str]:
    """Список поддерживаемых классов бетона."""
    return list(CONCRETE_GRADES)

def list_rebar_grades() -> List[str]:
    """Список поддерживаемых классов арматуры."""
    return list(TABLE_6_14_REBAR.keys())

def generate_code_snippet(concrete: Concrete, rebar: Rebar) -> str:
    """
    Генерирует готовый блок кода на Python для импорта и расчета выбранных материалов
    в произвольном инженерном блокноте Jupyter.
    """
    snippet = f"""# ==============================================================================
# Параметры материалов по СП 63.13330.2018 (сгенерировано автоматически)
# ==============================================================================
from sp63_materials import Concrete, Rebar

# 1. Бетон класса {concrete.grade}
concrete = Concrete(
    grade='{concrete.grade}',
    concrete_type='{concrete.concrete_type}',
    humidity='{concrete.humidity}',
    long_term={concrete.long_term},
    gamma_b1={concrete.gamma_b1},
    gamma_b2={concrete.gamma_b2},
    gamma_b3={concrete.gamma_b3},
    gamma_b4={concrete.gamma_b4},
    gamma_b5={concrete.gamma_b5}
)

# 2. Арматура класса {rebar.grade}
rebar = Rebar(
    grade='{rebar.grade}',
    long_term={rebar.long_term},
    gamma_s={rebar.gamma_s}
)

# 3. Основные расчетные константы для расчетов сечений:
Rb = concrete.Rb          # {concrete.Rb} МПа (расчетное сопротивление сжатию)
Rbt = concrete.Rbt        # {concrete.Rbt} МПа (расчетное сопротивление растяжению)
Eb = concrete.Eb_red      # {concrete.Eb_red} МПа (приведенный/эффективный модуль)
Rs = rebar.Rs             # {rebar.Rs} МПа (расчетное сопротивление арматуры растяжению)
Rsc = rebar.Rsc           # {rebar.Rsc} МПа (расчетное сопротивление арматуры сжатию)
Es = rebar.Es             # {rebar.Es} МПа (модуль упругости арматуры)

print(f"Материалы настроены: Бетон {{concrete.grade}} (Rb={{Rb}} МПа), Арматура {{rebar.grade}} (Rs={{Rs}} МПа)")
"""
    return snippet
