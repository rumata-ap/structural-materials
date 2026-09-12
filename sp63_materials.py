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
    'B3.5', 'B5', 'B7.5', 'B10', 'B12.5', 'B15', 'B20', 'B25',
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
    '>75%':   {'eps_b0': 0.0030, 'eps_b2': 0.0042, 'eps_bt0': 0.00021, 'eps_bt2': 0.00027},
    '40-75%': {'eps_b0': 0.0034, 'eps_b2': 0.0048, 'eps_bt0': 0.00024, 'eps_bt2': 0.00031},
    '<40%':   {'eps_b0': 0.0040, 'eps_b2': 0.0056, 'eps_bt0': 0.00028, 'eps_bt2': 0.00036}
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
    'K1400': 1400.0,
    'K1500': 1500.0,
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
    'K1400': {'Rs': 1170.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
    'K1500': {'Rs': 1250.0, 'Rsc_short': 400.0, 'Rsc_long': 500.0},
}

# Таблица 6.15: Поперечная арматура Rsw, МПа
TABLE_6_15_RSW = {
    'A240': 170.0,
    'A400': 280.0,
    'A500': 300.0,
    'B500': 300.0,
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
    ):
        grade_clean = grade.strip().upper()
        if not grade_clean.startswith('B'):
            grade_clean = 'B' + grade_clean
        if grade_clean not in TABLE_6_8_RB:
            raise ValueError(f"Неизвестный класс бетона: '{grade}'. Доступные: {CONCRETE_GRADES}")

        self.grade = grade_clean
        self.concrete_type = concrete_type
        if humidity not in ['<40%', '40-75%', '>75%']:
            raise ValueError("humidity должен быть одним из: '<40%', '40-75%', '>75%'")
        self.humidity = humidity
        self.long_term = long_term

        # Автоматическое определение gamma_b1 при None
        if gamma_b1 is None:
            self.gamma_b1 = 0.90 if long_term else 1.00
        else:
            self.gamma_b1 = float(gamma_b1)

        self.gamma_b2 = float(gamma_b2)
        self.gamma_b3 = float(gamma_b3)
        self.gamma_b4 = float(gamma_b4)
        self.gamma_b5 = float(gamma_b5)

    @property
    def gamma_b_total(self) -> float:
        """Итоговый коэффициент условий работы для осевого сжатия Rb."""
        return self.gamma_b1 * self.gamma_b2 * self.gamma_b3 * self.gamma_b4 * self.gamma_b5

    @property
    def gamma_bt_total(self) -> float:
        """Итоговый коэффициент условий работы для осевого растяжения Rbt (без gamma_b3)."""
        return self.gamma_b1 * self.gamma_b2 * self.gamma_b4 * self.gamma_b5

    # Базовые нормативные и расчетные характеристики
    @property
    def Rbn(self) -> float:
        """Нормативное сопротивление осевому сжатию Rbn, МПа (табл. 6.7)."""
        return TABLE_6_7_RBN[self.grade]

    @property
    def Rbtn(self) -> float:
        """Нормативное сопротивление осевому растяжению Rbtn, МПа (табл. 6.7)."""
        return TABLE_6_7_RBTN[self.grade]

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
        return TABLE_6_8_RB[self.grade]

    @property
    def Rbt_base(self) -> float:
        """Базовое расчетное сопротивление растяжению Rbt без коэффициентов gamma_bi, МПа (табл. 6.8)."""
        return TABLE_6_8_RBT[self.grade]

    @property
    def Rb(self) -> float:
        """Расчетное сопротивление сжатию Rb с учетом коэффициентов gamma_bi, МПа."""
        return round(self.Rb_base * self.gamma_b_total, 3)

    @property
    def Rbt(self) -> float:
        """Расчетное сопротивление растяжению Rbt с учетом коэффициентов gamma_bi, МПа."""
        return round(self.Rbt_base * self.gamma_bt_total, 3)

    @property
    def Eb(self) -> float:
        """Начальный модуль упругости бетона Eb, МПа (табл. 6.11)."""
        return TABLE_6_11_EB[self.grade] * 1000.0

    @property
    def phi_b_cr(self) -> float:
        """Коэффициент ползучести бетона phi_b,cr (табл. 6.12)."""
        hum_dict = TABLE_6_12_PHI_CR[self.humidity]
        return hum_dict.get(self.grade, hum_dict['B60'])

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

    # Предельные относительные деформации бетона
    @property
    def eps_b0(self) -> float:
        """
        Относительная деформация при достижении максимального напряжения сжатия Rb (п. 6.1.14 / 6.1.20).
        """
        if self.long_term:
            return TABLE_6_10_DEFORMATIONS[self.humidity]['eps_b0']
        return 0.0020

    @property
    def eps_b2(self) -> float:
        """
        Предельная относительная деформация бетона при осевом сжатии (п. 6.1.14 / 6.1.20).
        """
        if self.long_term:
            return TABLE_6_10_DEFORMATIONS[self.humidity]['eps_b2']
        # Кратковременное действие
        grade_num = float(self.grade.replace('B', ''))
        if grade_num <= 60:
            return 0.0035
        # Для B70..B100 интерполяция от 0.0033 (B70) до 0.0028 (B100)
        return round(0.0033 - (grade_num - 70.0) / 30.0 * (0.0033 - 0.0028), 5)

    @property
    def eps_bt0(self) -> float:
        """Относительная деформация при достижении Rbt при растяжении (п. 6.1.14 / 6.1.22)."""
        if self.long_term:
            return TABLE_6_10_DEFORMATIONS[self.humidity]['eps_bt0']
        return 0.00010

    @property
    def eps_bt2(self) -> float:
        """Предельная относительная деформация бетона при осевом растяжении (п. 6.1.14 / 6.1.22)."""
        if self.long_term:
            return TABLE_6_10_DEFORMATIONS[self.humidity]['eps_bt2']
        return 0.00015

    # --------------------------------------------------------------------------
    # Деформационные диаграммы
    # --------------------------------------------------------------------------

    def get_diagram(
        self,
        model: str = 'bilinear',
        state: str = 'compression',
        n_points: int = 100
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
        is_comp = (state.lower() == 'compression')
        R = self.Rb if is_comp else self.Rbt
        eps0 = self.eps_b0 if is_comp else self.eps_bt0
        eps2 = self.eps_b2 if is_comp else self.eps_bt2
        E = self.Eb_red

        model_clean = model.lower()

        if model_clean == 'bilinear':
            # Двухлинейная диаграмма (п. 6.1.21):
            # 0 <= eps <= eps0: sigma = (R / eps0) * eps
            # eps0 < eps <= eps2: sigma = R
            eps_arr = np.linspace(0.0, eps2, n_points)
            sigma_arr = np.piecewise(
                eps_arr,
                [eps_arr <= eps0, eps_arr > eps0],
                [lambda e: (R / eps0) * e, lambda e: R]
            )

        elif model_clean == 'trilinear':
            # Трехлинейная диаграмма (п. 6.1.20):
            # Точка 1: sigma1 = 0.6 * R, eps1 = 0.6 * R / (0.85 * E)
            # Точка 0: sigma0 = R, eps0
            # Точка 2: sigma2 = R, eps2
            sigma1 = 0.6 * R
            E1 = 0.85 * E
            eps1 = sigma1 / E1
            if eps1 >= eps0:
                eps1 = 0.6 * eps0

            eps_arr = np.linspace(0.0, eps2, n_points)
            sigma_arr = np.zeros_like(eps_arr)
            for i, e in enumerate(eps_arr):
                if e <= eps1:
                    sigma_arr[i] = (sigma1 / eps1) * e
                elif e <= eps0:
                    sigma_arr[i] = sigma1 + (R - sigma1) * (e - eps1) / (eps0 - eps1)
                else:
                    sigma_arr[i] = R

        elif model_clean == 'nonlinear':
            # Криволинейная нелинейная диаграмма (Приложение Г, формулы Г.1-Г.4)
            # sigma = (1 - eta * omega) * Eb * eps
            # где omega = eps / eps0, а на нисходящей ветке до eps2:
            eps_arr = np.linspace(0.0, eps2, n_points)
            sigma_arr = np.zeros_like(eps_arr)
            for i, e in enumerate(eps_arr):
                if e <= eps0:
                    # Восходящая ветвь: плавная квадратично-дробная аппроксимация
                    eta = e / eps0
                    k = 1.1 * (E * eps0) / max(R, 0.01)
                    denom = 1.0 + (k - 2.0) * eta
                    if abs(denom) < 1e-4:
                        denom = 1e-4
                    sigma_arr[i] = R * (k * eta - eta**2) / denom
                else:
                    # Горизонтальная площадка до предельных деформаций eps2
                    sigma_arr[i] = R
            sigma_arr = np.clip(sigma_arr, 0.0, R)

        else:
            raise ValueError(f"Неизвестная модель диаграммы: '{model}'. Выберите 'bilinear', 'trilinear' или 'nonlinear'.")

        return eps_arr, sigma_arr

    def to_dict(self) -> Dict[str, Union[str, float, bool]]:
        """Сводный словарь всех характеристик бетона."""
        return {
            'grade': self.grade,
            'concrete_type': self.concrete_type,
            'humidity': self.humidity,
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
            'eps_b2': self.eps_b2,
            'eps_bt0': self.eps_bt0,
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
        grade_clean = grade.strip().upper()
        # Замена кириллического 'А' или 'В' на латинские 'A', 'B' при необходимости
        grade_clean = grade_clean.replace('А', 'A').replace('В', 'B').replace('К', 'K')
        if grade_clean not in TABLE_6_14_REBAR:
            raise ValueError(f"Неизвестный класс арматуры: '{grade}'. Доступные: {list(TABLE_6_14_REBAR.keys())}")

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
    def Es(self) -> float:
        """Модуль упругости арматуры Es, МПа (п. 6.2.12)."""
        if self.grade.startswith('K'):
            return 1.95e5
        return 2.0e5

    @property
    def eps_s0(self) -> float:
        """Относительная деформация при достижении предела текучести eps_s0 = Rs / Es."""
        return round(self.Rs / self.Es, 6)

    @property
    def eps_s2(self) -> float:
        """Предельная относительная деформация арматуры (п. 6.2.14)."""
        return 0.025

    # --------------------------------------------------------------------------
    # Деформационная диаграмма арматуры
    # --------------------------------------------------------------------------

    def get_diagram(
        self,
        model: str = 'prandtl',
        state: str = 'tension',
        n_points: int = 100
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
        is_tens = (state.lower() == 'tension')
        R = self.Rs if is_tens else self.Rsc
        eps0 = R / self.Es
        eps2 = self.eps_s2

        eps_arr = np.linspace(0.0, eps2, n_points)
        sigma_arr = np.piecewise(
            eps_arr,
            [eps_arr <= eps0, eps_arr > eps0],
            [lambda e: self.Es * e, lambda e: R]
        )
        return eps_arr, sigma_arr

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
