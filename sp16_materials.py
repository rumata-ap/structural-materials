"""
sp16_materials.py
-----------------
Модуль для определения нормативных и расчетных характеристик материалов
стальных конструкций (прокатная сталь, болтовые соединения) и деформационных
диаграмм по СП 16.13330.2017 "Стальные конструкции. Актуализированная редакция
СНиП II-23-81*" (с Изменениями № 1 и № 2).

Разработчик: Antigravity AI Pair Programmer
Дата: 2026-09-12
"""

from typing import Dict, Tuple, List, Optional, Union
import numpy as np


# ==============================================================================
# ФИЗИЧЕСКИЕ КОНСТАНТЫ СТАЛИ (п. 5.1 СП 16.13330.2017)
# ==============================================================================
STEEL_E = 206000.0        # Модуль упругости E, МПа (2.06 * 10^5 МПа)
STEEL_G = 84000.0         # Модуль сдвига G, МПа (0.84 * 10^5 МПа)
STEEL_NU = 0.30           # Коэффициент Пуассона nu
STEEL_RHO = 7850.0        # Плотность стали rho, кг/м3
STEEL_ALPHA = 1.2e-5      # Коэффициент линейного расширения alpha, 1/°C


# ==============================================================================
# НОРМАТИВНЫЕ ТАБЛИЦЫ СП 16.13330.2017 (Приложение В)
# ==============================================================================

# Таблица В.5: Фасонный прокат по ГОСТ 27772
# Примечание *: за толщину фасонного проката принимается толщина полки t_f.
# Числитель: со статконтролем (gamma_m = 1.025)
# Знаменатель: без статконтроля (gamma_m = 1.050)
TABLE_B5_SHAPES = {
    'С245': [
        {'t_min': 4.0, 't_max': 20.0, 'Ryn': 245.0, 'Run': 370.0, 'Ry_stat': 240.0, 'Ry_nonstat': 235.0, 'Ru_stat': 360.0, 'Ru_nonstat': 350.0},
        {'t_min': 20.0, 't_max': 40.0, 'Ryn': 235.0, 'Run': 370.0, 'Ry_stat': 230.0, 'Ry_nonstat': 225.0, 'Ru_stat': 360.0, 'Ru_nonstat': 350.0},
    ],
    'С255': [
        {'t_min': 4.0, 't_max': 10.0, 'Ryn': 255.0, 'Run': 380.0, 'Ry_stat': 250.0, 'Ry_nonstat': 245.0, 'Ru_stat': 370.0, 'Ru_nonstat': 360.0},
        {'t_min': 10.0, 't_max': 20.0, 'Ryn': 245.0, 'Run': 370.0, 'Ry_stat': 240.0, 'Ry_nonstat': 235.0, 'Ru_stat': 360.0, 'Ru_nonstat': 350.0},
        {'t_min': 20.0, 't_max': 40.0, 'Ryn': 235.0, 'Run': 370.0, 'Ry_stat': 230.0, 'Ry_nonstat': 225.0, 'Ru_stat': 360.0, 'Ru_nonstat': 350.0},
    ],
    'С345': [
        {'t_min': 4.0, 't_max': 10.0, 'Ryn': 345.0, 'Run': 480.0, 'Ry_stat': 340.0, 'Ry_nonstat': 330.0, 'Ru_stat': 470.0, 'Ru_nonstat': 460.0},
        {'t_min': 10.0, 't_max': 20.0, 'Ryn': 325.0, 'Run': 470.0, 'Ry_stat': 320.0, 'Ry_nonstat': 310.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 20.0, 't_max': 40.0, 'Ryn': 305.0, 'Run': 460.0, 'Ry_stat': 300.0, 'Ry_nonstat': 290.0, 'Ru_stat': 450.0, 'Ru_nonstat': 440.0},
    ],
    'С345К': [
        {'t_min': 4.0, 't_max': 10.0, 'Ryn': 345.0, 'Run': 470.0, 'Ry_stat': 340.0, 'Ry_nonstat': 330.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
    ],
    'С355': [
        {'t_min': 8.0, 't_max': 16.0, 'Ryn': 355.0, 'Run': 490.0, 'Ry_stat': 350.0, 'Ry_nonstat': 340.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 16.0, 't_max': 40.0, 'Ryn': 345.0, 'Run': 480.0, 'Ry_stat': 340.0, 'Ry_nonstat': 330.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
    ],
    'С355-1': [
        {'t_min': 8.0, 't_max': 16.0, 'Ryn': 355.0, 'Run': 490.0, 'Ry_stat': 350.0, 'Ry_nonstat': 340.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 16.0, 't_max': 40.0, 'Ryn': 345.0, 'Run': 480.0, 'Ry_stat': 340.0, 'Ry_nonstat': 330.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
    ],
    'С390': [
        {'t_min': 8.0, 't_max': 10.0, 'Ryn': 390.0, 'Run': 520.0, 'Ry_stat': 380.0, 'Ry_nonstat': 370.0, 'Ru_stat': 505.0, 'Ru_nonstat': 495.0},
        {'t_min': 10.0, 't_max': 20.0, 'Ryn': 380.0, 'Run': 500.0, 'Ry_stat': 370.0, 'Ry_nonstat': 360.0, 'Ru_stat': 480.0, 'Ru_nonstat': 475.0},
        {'t_min': 20.0, 't_max': 40.0, 'Ryn': 370.0, 'Run': 490.0, 'Ry_stat': 360.0, 'Ry_nonstat': 350.0, 'Ru_stat': 480.0, 'Ru_nonstat': 470.0},
    ]
}

# Таблица В.3: Листовой, сортовой прокат и трубы
TABLE_B3_PLATES_TUBES = {
    'С235': [
        {'t_min': 2.0, 't_max': 4.0, 'Ryn': 235.0, 'Run': 360.0, 'Ry_stat': 230.0, 'Ry_nonstat': 225.0, 'Ru_stat': 350.0, 'Ru_nonstat': 345.0},
    ],
    'С245': [
        {'t_min': 2.0, 't_max': 20.0, 'Ryn': 245.0, 'Run': 370.0, 'Ry_stat': 240.0, 'Ry_nonstat': 235.0, 'Ru_stat': 360.0, 'Ru_nonstat': 350.0},
    ],
    'С255': [
        {'t_min': 2.0, 't_max': 3.9, 'Ryn': 255.0, 'Run': 380.0, 'Ry_stat': 250.0, 'Ry_nonstat': 245.0, 'Ru_stat': 370.0, 'Ru_nonstat': 360.0},
        {'t_min': 3.9, 't_max': 10.0, 'Ryn': 245.0, 'Run': 380.0, 'Ry_stat': 240.0, 'Ry_nonstat': 235.0, 'Ru_stat': 370.0, 'Ru_nonstat': 360.0},
        {'t_min': 10.0, 't_max': 20.0, 'Ryn': 245.0, 'Run': 370.0, 'Ry_stat': 240.0, 'Ry_nonstat': 235.0, 'Ru_stat': 360.0, 'Ru_nonstat': 350.0},
        {'t_min': 20.0, 't_max': 40.0, 'Ryn': 235.0, 'Run': 370.0, 'Ry_stat': 230.0, 'Ry_nonstat': 225.0, 'Ru_stat': 360.0, 'Ru_nonstat': 350.0},
    ],
    'С345': [
        {'t_min': 2.0, 't_max': 10.0, 'Ryn': 345.0, 'Run': 490.0, 'Ry_stat': 340.0, 'Ry_nonstat': 330.0, 'Ru_stat': 480.0, 'Ru_nonstat': 470.0},
    ],
    'С345К': [
        {'t_min': 4.0, 't_max': 10.0, 'Ryn': 345.0, 'Run': 470.0, 'Ry_stat': 340.0, 'Ry_nonstat': 330.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
    ],
    'С355': [
        {'t_min': 8.0, 't_max': 16.0, 'Ryn': 355.0, 'Run': 490.0, 'Ry_stat': 350.0, 'Ry_nonstat': 340.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 16.0, 't_max': 40.0, 'Ryn': 345.0, 'Run': 490.0, 'Ry_stat': 340.0, 'Ry_nonstat': 330.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 40.0, 't_max': 60.0, 'Ryn': 335.0, 'Run': 490.0, 'Ry_stat': 330.0, 'Ry_nonstat': 320.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 60.0, 't_max': 80.0, 'Ryn': 325.0, 'Run': 490.0, 'Ry_stat': 320.0, 'Ry_nonstat': 310.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 80.0, 't_max': 100.0, 'Ryn': 315.0, 'Run': 470.0, 'Ry_stat': 310.0, 'Ry_nonstat': 300.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 100.0, 't_max': 160.0, 'Ryn': 295.0, 'Run': 470.0, 'Ry_stat': 285.0, 'Ry_nonstat': 280.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
    ],
    'С355-1': [
        {'t_min': 8.0, 't_max': 16.0, 'Ryn': 345.0, 'Run': 490.0, 'Ry_stat': 350.0, 'Ry_nonstat': 340.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 16.0, 't_max': 40.0, 'Ryn': 345.0, 'Run': 490.0, 'Ry_stat': 340.0, 'Ry_nonstat': 330.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
        {'t_min': 40.0, 't_max': 50.0, 'Ryn': 335.0, 'Run': 490.0, 'Ry_stat': 330.0, 'Ry_nonstat': 320.0, 'Ru_stat': 460.0, 'Ru_nonstat': 450.0},
    ],
    'С390': [
        {'t_min': 8.0, 't_max': 50.0, 'Ryn': 390.0, 'Run': 520.0, 'Ry_stat': 380.0, 'Ry_nonstat': 370.0, 'Ru_stat': 505.0, 'Ru_nonstat': 495.0},
    ],
    'С440': [
        {'t_min': 8.0, 't_max': 50.0, 'Ryn': 440.0, 'Run': 540.0, 'Ry_stat': 430.0, 'Ry_nonstat': 420.0, 'Ru_stat': 525.0, 'Ru_nonstat': 515.0},
    ],
    'С550': [
        {'t_min': 8.0, 't_max': 50.0, 'Ryn': 540.0, 'Run': 640.0, 'Ry_stat': 525.0, 'Ry_nonstat': 515.0, 'Ru_stat': 625.0, 'Ru_nonstat': 610.0},
    ],
    'С590': [
        {'t_min': 8.0, 't_max': 50.0, 'Ryn': 590.0, 'Run': 685.0, 'Ry_stat': 575.0, 'Ry_nonstat': 560.0, 'Ru_stat': 670.0, 'Ru_nonstat': 650.0},
    ]
}

# Таблица В.4: Двутавры с параллельными гранями полок по ГОСТ Р 57837
TABLE_B4_PARALLEL_BEAMS = {
    'С255Б': [
        {'t_min': 0.0, 't_max': 10.0, 'Ryn': 255.0, 'Run': 380.0, 'Ry': 250.0, 'Ru': 370.0},
        {'t_min': 10.0, 't_max': 20.0, 'Ryn': 245.0, 'Run': 370.0, 'Ry': 240.0, 'Ru': 360.0},
        {'t_min': 20.0, 't_max': 40.0, 'Ryn': 235.0, 'Run': 370.0, 'Ry': 230.0, 'Ru': 360.0},
        {'t_min': 40.0, 't_max': 60.0, 'Ryn': 235.0, 'Run': 370.0, 'Ry': 230.0, 'Ru': 360.0},
        {'t_min': 60.0, 't_max': 80.0, 'Ryn': 225.0, 'Run': 370.0, 'Ry': 220.0, 'Ru': 360.0},
        {'t_min': 80.0, 't_max': 100.0, 'Ryn': 215.0, 'Run': 370.0, 'Ry': 210.0, 'Ru': 360.0},
        {'t_min': 100.0, 't_max': 150.0, 'Ryn': 200.0, 'Run': 360.0, 'Ry': 195.0, 'Ru': 350.0},
    ],
    'С345Б': [
        {'t_min': 0.0, 't_max': 10.0, 'Ryn': 345.0, 'Run': 480.0, 'Ry': 335.0, 'Ru': 470.0},
        {'t_min': 10.0, 't_max': 20.0, 'Ryn': 325.0, 'Run': 470.0, 'Ry': 315.0, 'Ru': 460.0},
        {'t_min': 20.0, 't_max': 40.0, 'Ryn': 305.0, 'Run': 460.0, 'Ry': 300.0, 'Ru': 450.0},
        {'t_min': 40.0, 't_max': 60.0, 'Ryn': 285.0, 'Run': 450.0, 'Ry': 280.0, 'Ru': 440.0},
    ],
    'С355Б': [
        {'t_min': 0.0, 't_max': 20.0, 'Ryn': 355.0, 'Run': 470.0, 'Ry': 345.0, 'Ru': 460.0},
        {'t_min': 20.0, 't_max': 40.0, 'Ryn': 345.0, 'Run': 470.0, 'Ry': 335.0, 'Ru': 460.0},
        {'t_min': 40.0, 't_max': 60.0, 'Ryn': 335.0, 'Run': 470.0, 'Ry': 325.0, 'Ru': 460.0},
        {'t_min': 60.0, 't_max': 80.0, 'Ryn': 325.0, 'Run': 460.0, 'Ry': 315.0, 'Ru': 450.0},
        {'t_min': 80.0, 't_max': 100.0, 'Ryn': 315.0, 'Run': 460.0, 'Ry': 305.0, 'Ru': 450.0},
        {'t_min': 100.0, 't_max': 150.0, 'Ryn': 295.0, 'Run': 460.0, 'Ry': 290.0, 'Ru': 450.0},
    ],
    'С390Б': [
        {'t_min': 0.0, 't_max': 30.0, 'Ryn': 390.0, 'Run': 520.0, 'Ry': 380.0, 'Ru': 505.0},
        {'t_min': 30.0, 't_max': 60.0, 'Ryn': 370.0, 'Run': 490.0, 'Ry': 360.0, 'Ru': 480.0},
        {'t_min': 60.0, 't_max': 80.0, 'Ryn': 360.0, 'Run': 480.0, 'Ry': 350.0, 'Ru': 470.0},
        {'t_min': 80.0, 't_max': 100.0, 'Ryn': 350.0, 'Run': 480.0, 'Ry': 340.0, 'Ru': 470.0},
        {'t_min': 100.0, 't_max': 150.0, 'Ryn': 330.0, 'Run': 470.0, 'Ry': 320.0, 'Ru': 460.0},
    ],
    'С440Б': [
        {'t_min': 20.0, 't_max': 30.0, 'Ryn': 430.0, 'Run': 560.0, 'Ry': 420.0, 'Ru': 545.0},
        {'t_min': 30.0, 't_max': 80.0, 'Ryn': 420.0, 'Run': 520.0, 'Ry': 410.0, 'Ru': 505.0},
        {'t_min': 80.0, 't_max': 100.0, 'Ryn': 400.0, 'Run': 520.0, 'Ry': 390.0, 'Ru': 505.0},
        {'t_min': 100.0, 't_max': 150.0, 'Ryn': 380.0, 'Run': 500.0, 'Ry': 370.0, 'Ru': 490.0},
    ]
}

# Таблица В.6: Смятие торцевой поверхности Rp (МПа) в зависимости от Run
TABLE_B6_RP = {
    360.0: {'Rp_stat': 351.0, 'Rp_nonstat': 343.0, 'Rlp_stat': 176.0, 'Rlp_nonstat': 171.0},
    370.0: {'Rp_stat': 361.0, 'Rp_nonstat': 352.0, 'Rlp_stat': 180.0, 'Rlp_nonstat': 176.0},
    380.0: {'Rp_stat': 371.0, 'Rp_nonstat': 362.0, 'Rlp_stat': 185.0, 'Rlp_nonstat': 181.0},
    470.0: {'Rp_stat': 459.0, 'Rp_nonstat': 448.0, 'Rlp_stat': 229.0, 'Rlp_nonstat': 224.0},
    480.0: {'Rp_stat': 468.0, 'Rp_nonstat': 457.0, 'Rlp_stat': 234.0, 'Rlp_nonstat': 228.0},
    490.0: {'Rp_stat': 478.0, 'Rp_nonstat': 467.0, 'Rlp_stat': 239.0, 'Rlp_nonstat': 233.0},
    500.0: {'Rp_stat': 488.0, 'Rp_nonstat': 476.0, 'Rlp_stat': 244.0, 'Rlp_nonstat': 238.0},
    520.0: {'Rp_stat': 507.0, 'Rp_nonstat': 495.0, 'Rlp_stat': 254.0, 'Rlp_nonstat': 248.0},
    540.0: {'Rp_stat': 527.0, 'Rp_nonstat': 514.0, 'Rlp_stat': 263.0, 'Rlp_nonstat': 257.0},
}

# Таблица Г.5: Расчетные сопротивления болтов в одноболтовых соединениях (МПа)
TABLE_G5_BOLTS = {
    '5.6':  {'Rbun': 500.0, 'Rbyn': 300.0, 'Rbs': 210.0, 'Rbt': 225.0},
    '5.8':  {'Rbun': 500.0, 'Rbyn': 400.0, 'Rbs': 210.0, 'Rbt': None},
    '8.8':  {'Rbun': 830.0, 'Rbyn': 664.0, 'Rbs': 332.0, 'Rbt': 451.0},
    '10.9': {'Rbun': 1040.0, 'Rbyn': 936.0, 'Rbs': 416.0, 'Rbt': 728.0},
    '12.9': {'Rbun': 1220.0, 'Rbyn': 1098.0, 'Rbs': 427.0, 'Rbt': 854.0},
}

# Площади сечения болтов брутто A (мм2) и нетто по резьбе Abn (мм2) по ГОСТ
BOLT_AREAS = {
    12: {'A': 113.1, 'Abn': 84.3},
    16: {'A': 201.1, 'Abn': 157.0},
    20: {'A': 314.2, 'Abn': 245.0},
    24: {'A': 452.4, 'Abn': 353.0},
    27: {'A': 572.6, 'Abn': 459.0},
    30: {'A': 706.9, 'Abn': 561.0},
    36: {'A': 1017.9, 'Abn': 817.0}
}


# ==============================================================================
# КЛАСС ПРОКАТНОЙ СТАЛИ
# ==============================================================================

class StructuralSteel:
    """
    Класс характеристик прокатной стали по СП 16.13330.2017.

    Параметры
    ---------
    grade : str
        Марка стали (например 'С245', 'С255', 'С345', 'С355', 'С390', 'С440').
    profile_type : str
        Вид проката:
        - 'shapes': фасонный прокат (уголки, швеллеры по ГОСТ 27772, табл. В.5).
                    За толщину принимается толщина полки t_f.
        - 'plates': листовой и универсальный прокат (табл. В.3).
        - 'tubes': трубы круглые и профильные (табл. В.3).
        - 'beams_parallel': двутавры с параллельными гранями полок (ГОСТ Р 57837, табл. В.4).
    thickness : float
        Толщина проката (или толщина полки t_f для фасонного), мм.
    statistical_control : bool
        True (по умолчанию) - прокат со статистическим контролем свойств (чиститель, gamma_m = 1.025).
        False - прокат без статистического контроля (знаменатель, gamma_m = 1.050).
    gamma_c : float
        Коэффициент условий работы по Таблице 1 СП 16 (по умолчанию 1.0).
    """

    def __init__(
        self,
        grade: str = 'С255',
        profile_type: str = 'shapes',
        thickness: float = 12.0,
        statistical_control: bool = True,
        gamma_c: float = 1.0,
    ):
        grade_clean = grade.strip().upper().replace('C', 'С') # замена латинской C на русскую С
        self.grade = grade_clean
        self.profile_type = profile_type.lower()
        self.thickness = float(thickness)
        self.statistical_control = statistical_control
        self.gamma_c = float(gamma_c)

        # Выбираем соответствующую нормативную таблицу
        self._row = self._resolve_table_row()

    def _resolve_table_row(self) -> Dict[str, float]:
        """Поиск строки нормативной таблицы с учетом типа проката, марки и толщины."""
        pt = self.profile_type
        t = self.thickness

        if pt == 'shapes':
            tbl = TABLE_B5_SHAPES
            if self.grade not in tbl:
                # Если марки нет в табл. В.5, проверяем табл. В.3
                tbl = TABLE_B3_PLATES_TUBES
        elif pt in ['plates', 'tubes']:
            tbl = TABLE_B3_PLATES_TUBES
        elif pt in ['beams_parallel', 'beams']:
            tbl = TABLE_B4_PARALLEL_BEAMS
            # Для балок марка может иметь суффикс 'Б' (например 'С255Б')
            alt_grade = self.grade if self.grade.endswith('Б') else (self.grade + 'Б')
            if alt_grade in tbl:
                self.grade = alt_grade
        else:
            raise ValueError(f"Неизвестный тип проката: '{self.profile_type}'. Выберите 'shapes', 'plates', 'tubes' или 'beams_parallel'.")

        if self.grade not in tbl:
            raise ValueError(f"Марка стали '{self.grade}' не найдена в нормативах для типа '{pt}'. Доступные: {list(tbl.keys())}")

        ranges = tbl[self.grade]
        for r in ranges:
            if r['t_min'] <= t <= r['t_max']:
                return r

        # Если толщина выходит за диапазон
        t_min_all = min(r['t_min'] for r in ranges)
        t_max_all = max(r['t_max'] for r in ranges)
        raise ValueError(
            f"Толщина {t} мм вне допустимого диапазона [{t_min_all}, {t_max_all}] мм для стали {self.grade} ({self.profile_type})."
        )

    # --------------------------------------------------------------------------
    # Нормативные сопротивления (МПа / Н/мм2)
    # --------------------------------------------------------------------------
    @property
    def Ryn(self) -> float:
        """Нормативный предел текучести Ryn, МПа."""
        return self._row['Ryn']

    @property
    def Run(self) -> float:
        """Нормативное временное сопротивление (предел прочности) Run, МПа."""
        return self._row['Run']

    # --------------------------------------------------------------------------
    # Базовые расчетные сопротивления без gamma_c (МПа / Н/мм2)
    # --------------------------------------------------------------------------
    @property
    def Ry_base(self) -> float:
        """Базовое расчетное сопротивление по пределу текучести Ry, МПа."""
        if 'Ry' in self._row:
            return self._row['Ry']
        return self._row['Ry_stat'] if self.statistical_control else self._row['Ry_nonstat']

    @property
    def Ru_base(self) -> float:
        """Базовое расчетное сопротивление по пределу прочности Ru, МПа."""
        if 'Ru' in self._row:
            return self._row['Ru']
        return self._row['Ru_stat'] if self.statistical_control else self._row['Ru_nonstat']

    # --------------------------------------------------------------------------
    # Итоговые расчетные сопротивления с учетом gamma_c (МПа)
    # --------------------------------------------------------------------------
    @property
    def Ry(self) -> float:
        """Расчетное сопротивление растяжению, сжатию и изгибу Ry = Ry_base * gamma_c, МПа."""
        return round(self.Ry_base * self.gamma_c, 1)

    @property
    def Ru(self) -> float:
        """Расчетное сопротивление по пределу прочности Ru = Ru_base * gamma_c, МПа."""
        return round(self.Ru_base * self.gamma_c, 1)

    @property
    def Rs(self) -> float:
        """Расчетное сопротивление сдвигу Rs = 0.58 * Ry, МПа (п. 5.3 СП 16)."""
        return round(0.58 * self.Ry, 1)

    @property
    def Rp(self) -> float:
        """
        Расчетное сопротивление смятию торцевой поверхности при наличии пригонки Rp, МПа (Таблица В.6).
        """
        run = self.Run
        if run in TABLE_B6_RP:
            key = 'Rp_stat' if self.statistical_control else 'Rp_nonstat'
            return round(TABLE_B6_RP[run][key] * self.gamma_c, 1)
        # Приближенная интерполяция по Таблице В.6 при нестандартном Run
        return round(self.Run * (0.975 if self.statistical_control else 0.952) * self.gamma_c, 1)

    @property
    def Rlp(self) -> float:
        """Расчетное сопротивление местному смятию в цилиндрических шарнирах Rlp = 0.5 * Ry, МПа."""
        return round(0.50 * self.Ry, 1)

    @property
    def Rcd(self) -> float:
        """Расчетное сопротивление диаметральному сжатию катков Rcd = 0.025 * Ru, МПа."""
        return round(0.025 * self.Ru, 1)

    # --------------------------------------------------------------------------
    # Физические свойства
    # --------------------------------------------------------------------------
    @property
    def E(self) -> float:
        """Модуль упругости стали E = 206 000 МПа (п. 5.1)."""
        return STEEL_E

    @property
    def G(self) -> float:
        """Модуль сдвига стали G = 84 000 МПа (п. 5.1)."""
        return STEEL_G

    @property
    def nu(self) -> float:
        """Коэффициент Пуассона nu = 0.30."""
        return STEEL_NU

    @property
    def rho(self) -> float:
        """Плотность стали rho = 7850 кг/м3."""
        return STEEL_RHO

    @property
    def eps_y(self) -> float:
        """Относительная деформация предела текучести eps_y = Ry / E."""
        return round(self.Ry / self.E, 6)

    # --------------------------------------------------------------------------
    # Деформационная диаграмма состояния стали
    # --------------------------------------------------------------------------
    def get_diagram(
        self,
        model: str = 'prandtl',
        n_points: int = 100,
        eps_max: float = 0.025
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Построение диаграммы деформирования стали sigma - eps (п. 4.2.7 и Таблица В.9).

        Параметры
        ---------
        model : str
            'prandtl' (упруго-идеальнопластическая диаграмма Прандтля),
            'hardening' (диаграмма с линейным упрочнением за площадкой текучести).
        n_points : int
            Количество расчетных точек.
        eps_max : float
            Максимальная деформация (по умолчанию 0.025 = 2.5%).
        """
        eps_y = self.eps_y
        eps_arr = np.linspace(0.0, eps_max, n_points)
        sigma_arr = np.zeros_like(eps_arr)

        if model.lower() == 'prandtl':
            sigma_arr = np.piecewise(
                eps_arr,
                [eps_arr <= eps_y, eps_arr > eps_y],
                [lambda e: self.E * e, lambda e: self.Ry]
            )
        elif model.lower() == 'hardening':
            # Линейное упрочнение: площадка текучести до eps_t = 2.5 * eps_y, далее подъем до Ru
            eps_t = 2.5 * eps_y
            E_hard = (self.Ru - self.Ry) / max(eps_max - eps_t, 1e-4)
            for i, e in enumerate(eps_arr):
                if e <= eps_y:
                    sigma_arr[i] = self.E * e
                elif e <= eps_t:
                    sigma_arr[i] = self.Ry
                else:
                    sigma_arr[i] = min(self.Ry + E_hard * (e - eps_t), self.Ru)
        else:
            raise ValueError(f"Неизвестная модель: '{model}'. Выберите 'prandtl' или 'hardening'.")

        return eps_arr, sigma_arr

    def to_dict(self) -> Dict[str, Union[str, float, bool]]:
        """Сводный словарь параметров стали."""
        return {
            'grade': self.grade,
            'profile_type': self.profile_type,
            'thickness_mm': self.thickness,
            'statistical_control': self.statistical_control,
            'gamma_c': self.gamma_c,
            'Ryn_MPa': self.Ryn,
            'Run_MPa': self.Run,
            'Ry_base_MPa': self.Ry_base,
            'Ru_base_MPa': self.Ru_base,
            'Ry_design_MPa': self.Ry,
            'Ru_design_MPa': self.Ru,
            'Rs_shear_MPa': self.Rs,
            'Rp_bearing_MPa': self.Rp,
            'Rlp_pin_MPa': self.Rlp,
            'Rcd_roller_MPa': self.Rcd,
            'E_MPa': self.E,
            'G_MPa': self.G,
            'eps_y': self.eps_y
        }

    def to_markdown(self) -> str:
        """Сводная таблица характеристик в формате Markdown."""
        d = self.to_dict()
        stat_str = "Со статконтролем (γm = 1.025)" if d['statistical_control'] else "Без статконтроля (γm = 1.050)"
        md = f"""### Характеристики стали **{d['grade']}** (СП 16.13330.2017)

* **Вид проката:** {d['profile_type']} (толщина $t = {d['thickness_mm']}$ мм)
* **Качество проката:** {stat_str}
* **Коэффициент условий работы:** $\\gamma_c = {d['gamma_c']}$

| Параметр | Обозначение | Значение | Ед. изм. |
|:---------|:-----------:|:--------:|:--------:|
| Расчетное сопротивление растяжению/сжатию/изгибу | $R_y$ | **{d['Ry_design_MPa']}** | МПа |
| Расчетное сопротивление по пределу прочности | $R_u$ | **{d['Ru_design_MPa']}** | МПа |
| Расчетное сопротивление сдвигу ($0.58 R_y$) | $R_s$ | **{d['Rs_shear_MPa']}** | МПа |
| Расчетное сопротивление смятию торцевой поверхности | $R_p$ | {d['Rp_bearing_MPa']} | МПа |
| Расчетное сопротивление смятию в шарнирах ($0.5 R_y$) | $R_{{lp}}$ | {d['Rlp_pin_MPa']} | МПа |
| Нормативный предел текучести | $R_{{yn}}$ | {d['Ryn_MPa']} | МПа |
| Нормативное временное сопротивление | $R_{{un}}$ | {d['Run_MPa']} | МПа |
| Модуль упругости | $E$ | {d['E_MPa']:,.0f} | МПа |
| Модуль сдвига | $G$ | {d['G_MPa']:,.0f} | МПа |
| Деформация предела текучести | $\\varepsilon_y$ | {d['eps_y']} | - |
"""
        return md


# ==============================================================================
# КЛАСС БОЛТОВЫХ СОЕДИНЕНИЙ (СП 16, Приложение Г)
# ==============================================================================

class SteelBolt:
    """
    Класс болтов нормальной и повышенной прочности по СП 16.13330.2017 (Таблицы Г.3, Г.4, Г.5).

    Параметры
    ---------
    grade : str
        Класс прочности болта ('5.6', '5.8', '8.8', '10.9', '12.9').
    diameter : int
        Номинальный диаметр резьбы, мм (12, 16, 20, 24, 27, 30, 36).
    gamma_b : float
        Коэффициент условий работы болтового соединения (п. 14.2.5, по умолчанию 1.0;
        например 0.9 для многоболтовых соединений).
    """

    def __init__(
        self,
        grade: str = '8.8',
        diameter: int = 20,
        gamma_b: float = 1.0
    ):
        grade_clean = grade.strip()
        if grade_clean not in TABLE_G5_BOLTS:
            raise ValueError(f"Неизвестный класс болта: '{grade}'. Доступные: {list(TABLE_G5_BOLTS.keys())}")
        if diameter not in BOLT_AREAS:
            raise ValueError(f"Неподдерживаемый диаметр болта: {diameter} мм. Доступные: {list(BOLT_AREAS.keys())}")

        self.grade = grade_clean
        self.diameter = diameter
        self.gamma_b = float(gamma_b)

        self._prop = TABLE_G5_BOLTS[self.grade]
        self._geo = BOLT_AREAS[self.diameter]

    @property
    def Rbun(self) -> float:
        """Нормативное временное сопротивление стали болта Rbun, МПа."""
        return self._prop['Rbun']

    @property
    def Rbyn(self) -> float:
        """Нормативный предел текучести стали болта Rbyn, МПа."""
        return self._prop['Rbyn']

    @property
    def Rbs(self) -> float:
        """Расчетное сопротивление срезу одного болта Rbs, МПа (табл. Г.5)."""
        return self._prop['Rbs']

    @property
    def Rbt(self) -> Optional[float]:
        """Расчетное сопротивление растяжению одного болта Rbt, МПа (табл. Г.5)."""
        return self._prop['Rbt']

    @property
    def A(self) -> float:
        """Номинальная площадь стержня болта брутто A, мм2."""
        return self._geo['A']

    @property
    def Abn(self) -> float:
        """Площадь сечения болта нетто (по резьбе) Abn, мм2."""
        return self._geo['Abn']

    def shear_capacity(self, n_shear_planes: int = 1) -> float:
        """
        Несущая способность одного болта на срез Nbs = Rbs * A * n_s * gamma_b, кН (п. 14.2.5).
        """
        return round(self.Rbs * self.A * n_shear_planes * self.gamma_b / 1000.0, 2)

    def tension_capacity(self) -> Optional[float]:
        """
        Несущая способность одного болта на растяжение Nbt = Rbt * Abn * gamma_b, кН (п. 14.2.5).
        """
        if self.Rbt is None:
            return None
        return round(self.Rbt * self.Abn * self.gamma_b / 1000.0, 2)

    def to_dict(self) -> Dict[str, Union[str, float, None]]:
        """Сводный словарь параметров болта."""
        return {
            'grade': self.grade,
            'diameter_mm': self.diameter,
            'gamma_b': self.gamma_b,
            'Rbun_MPa': self.Rbun,
            'Rbyn_MPa': self.Rbyn,
            'Rbs_MPa': self.Rbs,
            'Rbt_MPa': self.Rbt,
            'A_mm2': self.A,
            'Abn_mm2': self.Abn,
            'Nbs_1plane_kN': self.shear_capacity(1),
            'Nbt_kN': self.tension_capacity()
        }

    def to_markdown(self) -> str:
        """Сводная таблица параметров болта в формате Markdown."""
        d = self.to_dict()
        rbt_str = f"{d['Rbt_MPa']} МПа" if d['Rbt_MPa'] is not None else "Не применяется на растяжение"
        nbt_str = f"{d['Nbt_kN']} кН" if d['Nbt_kN'] is not None else "-"
        md = f"""### Болт класса прочности **{d['grade']}**, М{d['diameter_mm']} (СП 16.13330.2017)

| Параметр | Обозначение | Значение | Ед. изм. |
|:---------|:-----------:|:--------:|:--------:|
| Расчетное сопротивление срезу | $R_{{bs}}$ | **{d['Rbs_MPa']}** | МПа |
| Расчетное сопротивление растяжению | $R_{{bt}}$ | **{rbt_str}** | - |
| Площадь стержня брутто | $A$ | {d['A_mm2']} | мм² |
| Площадь сечения нетто по резьбе | $A_{{bn}}$ | {d['Abn_mm2']} | мм² |
| Несущая способность на срез (1 плоскость) | $N_{{bs}}$ | **{d['Nbs_1plane_kN']}** | кН |
| Несущая способность на растяжение | $N_{{bt}}$ | **{nbt_str}** | кН |
| Коэффициент условий работы соединения | $\\gamma_b$ | {d['gamma_b']} | - |
"""
        return md


# ==============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И ГЕНЕРАТОР СНИППЕТОВ
# ==============================================================================

def list_steel_grades(profile_type: str = 'shapes') -> List[str]:
    """Список поддерживаемых марок стали для указанного вида проката."""
    if profile_type == 'shapes':
        return list(TABLE_B5_SHAPES.keys())
    elif profile_type in ['plates', 'tubes']:
        return list(TABLE_B3_PLATES_TUBES.keys())
    elif profile_type in ['beams_parallel', 'beams']:
        return list(TABLE_B4_PARALLEL_BEAMS.keys())
    return list(TABLE_B5_SHAPES.keys())

def generate_steel_code_snippet(steel: StructuralSteel, bolt: Optional[SteelBolt] = None) -> str:
    """Генерация готового кода для вставки в расчетный блокнот."""
    snippet = f"""# ==============================================================================
# Параметры стали по СП 16.13330.2017 (сгенерировано автоматически)
# ==============================================================================
from sp16_materials import StructuralSteel, SteelBolt

# 1. Прокатная сталь {steel.grade}
steel = StructuralSteel(
    grade='{steel.grade}',
    profile_type='{steel.profile_type}',
    thickness={steel.thickness},
    statistical_control={steel.statistical_control},
    gamma_c={steel.gamma_c}
)

# Расчетные сопротивления стали:
Ry = steel.Ry   # {steel.Ry} МПа (растяжение, сжатие, изгиб)
Ru = steel.Ru   # {steel.Ru} МПа (предел прочности)
Rs = steel.Rs   # {steel.Rs} МПа (сдвиг)
E  = steel.E    # {steel.E:,.0f} МПа (модуль упругости)
"""
    if bolt:
        snippet += f"""
# 2. Болтовое соединение (Болт кл. {bolt.grade}, М{bolt.diameter})
bolt = SteelBolt(
    grade='{bolt.grade}',
    diameter={bolt.diameter},
    gamma_b={bolt.gamma_b}
)
Rbs = bolt.Rbs   # {bolt.Rbs} МПа (расчетное сопротивление срезу)
Nbs = bolt.shear_capacity(n_shear_planes=1)  # {bolt.shear_capacity(1)} кН
"""
    return snippet
