# Нормативная библиотека материалов (СП 15.13330 / СП 16.13330 / СП 63.13330 / СП 64.13330)

Библиотека и интерактивные блокноты для выбора и расчета нормативных и расчетных характеристик строительных материалов в соответствии с актуальными российскими строительными сводами правил.

📖 **Онлайн-документация**: [https://structural-materials.readthedocs.io/](https://structural-materials.readthedocs.io/)  
[![PyPI](https://img.shields.io/pypi/v/structural-materials.svg)](https://pypi.org/project/structural-materials/)
[![Python Versions](https://img.shields.io/pypi/pyversions/structural-materials.svg)](https://pypi.org/project/structural-materials/)
[![Documentation Status](https://readthedocs.org/projects/structural-materials/badge/?version=latest)](https://structural-materials.readthedocs.io/ru/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Структура проекта

```text
structural-materials/
├── docs/                         # Исходники документации Sphinx
├── structural_materials/         # Пакет Python (СП 15, СП 16, СП 63, СП 64)
│   ├── __init__.py               # Экспорт ключевых классов и модулей
│   ├── sp15_materials.py         # СП 15.13330 (каменные и армокаменные)
│   ├── sp16_materials.py         # СП 16.13330 (сталь и болты)
│   ├── sp63_materials.py         # СП 63.13330 (бетон и арматура)
│   ├── sp64_materials.py         # СП 64.13330 (деревянные конструкции)
│   └── sp15_tables_data.json
├── notebooks/                    # Интерактивные блокноты Jupyter
│   ├── masonry_selector.ipynb
│   ├── material_selector.ipynb
│   ├── steel_selector.ipynb
│   └── wood_selector.ipynb
├── scripts/                      # Вспомогательные скрипты и генераторы
│   ├── build_dist.py             # Сборка пакетов wheel и sdist
│   ├── upload_to_pypi.py         # Публикация пакета на PyPI
│   ├── create_masonry_nb.py
│   ├── create_nb.py
│   └── create_steel_nb.py
├── tests/                        # Модульные тесты
│   ├── conftest.py
│   ├── test_notebook_generators.py
│   ├── test_sp15_materials.py
│   ├── test_sp16_materials.py
│   ├── test_sp63_materials.py
│   └── test_sp64_materials.py
├── .readthedocs.yaml             # Конфигурация Read the Docs
├── .github/workflows/docs.yml    # Автодеплой документации на GitHub Pages
├── LICENSE                       # Лицензия MIT
└── pyproject.toml                # Конфигурация пакета и сборщика
```

### Установка пакета

Установка стабильной версии из PyPI:

```bash
pip install structural-materials
```

Установка из репозитория в режиме разработки:

```bash
git clone https://github.com/rumata-ap/structural-materials.git
cd structural-materials
pip install -e .
```

---

## 1. СП 63.13330.2018 «Бетонные и железобетонные конструкции»

* **Модуль `sp63_materials.py`**:
  - Таблицы 6.7, 6.8, 6.10, 6.11, 6.12 (Бетон: $R_b, R_{bt}, R_{bn}, R_{btn}, E_b, \varphi_{b,cr}, E_{b,red}, \varepsilon_{b0}, \varepsilon_{b2}$).
  - Коэффициенты условий работы $\gamma_{b1} \dots \gamma_{b5}$.
  - Таблицы 6.13, 6.14, 6.15 (Арматура: $R_s, R_{sc}, R_{sn}, R_{sw}, E_s, \varepsilon_{s0}, \varepsilon_{s2}$).
  - Поддержаны тяжелый, мелкозернистый, легкий, поризованный, ячеистый и напрягающий бетон с обязательными контекстными параметрами для специальных видов.
  - Деформационные диаграммы: двухлинейная (п. 6.1.21), трехлинейная (п. 6.1.20) и нелинейная (Приложение Г); `get_diagram_points` возвращает именованные нормативные узлы.
* **Блокнот `beton_armatura_selector.ipynb`**:
  - Интерактивный подбор на `ipywidgets`, отрисовка графиков $\sigma - \varepsilon$ и генерация кода.

---

## 2. СП 16.13330.2017 «Стальные конструкции»

* **Модуль `sp16_materials.py`**:
  - **Таблица В.5**: Фасонный прокат по ГОСТ 27772 (С235, С245, С255, С345, С355, С390, С440, С590).
    - *Сноска \**: Толщина $t$ принимается строго по **толщине полки** ($t_f$).
    - *Сноска \*\*\**: Численные значения с учетом статистического контроля качества ($\gamma_m = 1{,}025$ — числитель) и без него ($\gamma_m = 1{,}050$ — знаменатель).
  - **Таблицы В.3, В.4 и В.5**: полный реализованный набор профилей и толщин с точными границами интервалов, включая открытый интервал В.4 `>100 мм`.
  - **Таблица В.6**: табличные расчетные сопротивления смятию торцевой поверхности ($R_p$), в шарнирах ($R_{lp}$) и катков ($R_{cd}$) без запрещенной интерполяции.
  - **Таблица 1**: полный каталог коэффициентов условий работы $\gamma_c = 0{,}75 \dots 1{,}20$.
  - **Таблицы Г.5 и Г.9**: классы болтов 5.6, 5.8, 8.8, 10.9, 12.9 и диаметры `М16, М18, М20, М22, М24, М27, М30, М36, М42, М48`; диаметры из скобок требуют `special_support=True`, М12 отсутствует.
  - Деформационные диаграммы вариантов `OBD`, `OACD`, `OACDEF` с именованными узлами Б.1 и нормировкой по группам В.9; совместимость с именами `prandtl`/`hardening` сохранена как явные псевдонимы.
* **Блокнот `steel_selector.ipynb`**:
  - Интерактивный выбор вида проката, марки стали, толщины до 160 мм, статистического контроля, значения $\gamma_c$ только из таблицы 1 и класса/диаметра болтов.
  - Построение выбранного варианта `OBD`/`OACD`/`OACDEF` с подписями всех узлов, а также гистограммы несущей способности болтов; отсутствие $N_{bt}$ не подменяется нулем.
  - Генераторы `create_nb.py` и `create_steel_nb.py` являются исходными артефактами структуры блокнотов и поддерживают явный аргумент пути вывода.

---

## 3. СП 15.13330.2020 «Каменные и армокаменные конструкции»

* **Модуль `sp15_materials.py`**:
  - Полные числовые каталоги таблиц 6.1–6.18: сопротивления сжатию, растяжению и срезу, коэффициенты условий работы, упругие характеристики, деформации и трение.
  - `Masonry` учитывает сноски к таблицам 6.1–6.3 и 6.9–6.10: тип раствора, подготовку образцов, пустотность, возраст раствора, паз-гребень, вибрирование и экспериментальные данные для клеевых составов.
  - `ReinforcedMasonry` реализует формулу (7.23), коэффициент пустотности $p$, $gamma_{cs}$ по таблице 6.14 и проверки применимости по пп. 7.31, 9.81а–9.83.
  - Деформационная диаграмма $σ-ε$, расчет $R_u$, $E_0$, $E_{strength}$ и $E_{stiffness}$, экспорт характеристик и готового кода в Markdown/Python.
* **Блокнот `masonry_selector.ipynb`**:
  - Интерактивный выбор вида кладки, марок и параметров сетки на `ipywidgets`.
  - Статический эталонный расчет кирпича М150/раствора М100 с графиком $σ-ε$, сводной таблицей и примером простенка 380 × 640 мм.
* **Тесты**: `pytest` или `pytest -v tests/test_sp15_materials.py`.

---

## 4. СП 64.13330.2017 «Деревянные конструкции»

* **Модуль `sp64_materials.py`**:
  - Нормативные и расчетные характеристики древесины и материалов на ее основе по СП 64.13330.2017 (в ред. Изменений № 1–4 от 28.12.2023).
  - `Timber`: цельная древесина по сортам 1, 2, 3 и породам (сосна, ель, лиственница, береза, дуб и др.), учет геометрических размеров ($m_б, m_ш$).
  - `StrengthClassWood`: цельная древесина по классам прочности C14–C50, T9–T30, D18–D70 (Приложение В.3).
  - `Glulam`: клеёная древесина классов K16–K40 с учетом толщины слоев ($m_{сл}$) и высоты балки ($m_б$) (Приложение В.4).
  - `LVL`: брус клееный из шпона сортов 1/K45, 1/K40, 2/K35, 3/K30 (Таблицы В.2, В.2а, 7).
  - `Plywood` и `OSB3`: фанера марок ФСФ, ФК, ФБС и плиты ОСП-3 с учетом анизотропии и ориентации волокон.
  - `WoodContext`: гибкий расчет коэффициентов условий работы: классов условий эксплуатации (1а–4б), режимов длительности нагрузки (А–М), температуры $m_т$ и срока службы сооружения $m_{сс}$.
* **Блокнот `wood_selector.ipynb`**:
  - Интерактивный расчет и подбор деревянных элементов и плитных обшивок на `ipywidgets` с визуализацией характеристик и автоматической генерацией кода.
* **Тесты**: `pytest` или `pytest -v tests/test_sp64_materials.py`.

---

## 5. Онлайн-витрина блокнотов (nbviewer)

* [Просмотр wood_selector.ipynb](https://jupyter.propgs.ru/localfile/materials/wood_selector.ipynb)
* [Просмотр steel_selector.ipynb](https://jupyter.propgs.ru/localfile/materials/steel_selector.ipynb)
* [Просмотр beton_armatura_selector.ipynb](https://jupyter.propgs.ru/localfile/materials/beton_armatura_selector.ipynb)
* [Просмотр masonry_selector.ipynb](https://jupyter.propgs.ru/localfile/materials/masonry_selector.ipynb)
* [Каталог раздела materials](https://jupyter.propgs.ru/localfile/materials/)

---

## 6. Примеры использования в инженерном коде

```python
# Вариант 1: импорт напрямую из пакета
from structural_materials import (
    Concrete, Rebar,
    StructuralSteel, SteelBolt,
    Masonry,
    Timber, Glulam, LVL, WoodContext,
)

# --- Бетон и арматура (СП 63) ---
concrete = Concrete(grade='B25', humidity='40-75%', long_term=True)
rebar = Rebar(grade='A500')
print(f"Бетон B25: Rb = {concrete.Rb} МПа, Eb,red = {concrete.Eb_red} МПа")
print(f"Арматура A500: Rs = {rebar.Rs} МПа")

# --- Сталь и болты (СП 16) ---
steel = StructuralSteel(grade='С255', profile_type='shapes', thickness=14.0, statistical_control=True)
bolt = SteelBolt(grade='8.8', diameter=20, gamma_b=0.9)
print(f"Сталь С255 (tf=14 мм): Ry = {steel.Ry} МПа, Ru = {steel.Ru} МПа")
print(f"Болт 8.8 М20: срез Nbs = {bolt.shear_capacity(1):.1f} кН, растяжение Nbt = {bolt.tension_capacity():.1f} кН")

# --- Каменная кладка (СП 15) ---
masonry = Masonry('brick', 'M150', 'M100')
reinforced = masonry.with_mesh_reinforcement(d=4, s=50, c=2, s_vert=65)
print(f"Кладка: R = {masonry.R:.2f} МПа, Rsk = {reinforced.Rsk:.2f} МПа")

# --- Деревянные конструкции (СП 64) ---
# Режим А (кратковременная/снеговая), отапливаемое помещение (класс 1а)
ctx = WoodContext(load_duration="А", service_class="1а")

timber = Timber(sort=2, species="pine", geometry_case="rectangular_edge_h_le_500", context=ctx)
print(f"Сосна 2 сорт: R_изгиб = {timber.resistance('bending'):.2f} МПа, E = {timber.E_mean_MPa} МПа")

glulam = Glulam(grade="K24", context=ctx, layer_thickness_mm=33.0, h_mm=600.0)
print(f"Glulam K24: R_изгиб = {glulam.resistance('bending'):.2f} МПа, E = {glulam.E_mean_MPa} МПа")

lvl = LVL(grade="1/K45", context=ctx)
print(f"LVL 1/K45: R_изгиб = {lvl.resistance('bending'):.2f} МПа, E = {lvl.E_mean_MPa} МПа")
```
