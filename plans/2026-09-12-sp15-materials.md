# СП 15.13330.2020 Masonry Materials Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реализовать модуль материалов `sp15_materials.py`, эталонный набор unit-тестов `test_sp15_materials.py`, интерактивный расчетный блокнот `masonry_selector.ipynb`, установить модуль в контейнер Jupyter на сервере `debian-13-6` и верифицировать отрендеренный блокнот на витрине `nbviewer`.

**Architecture:** Единая объектная модель на классах `Masonry` и `ReinforcedMasonry`, инкапсулирующая 18 нормативных таблиц СП 15.13330.2020 (с Изменением № 1) со строгим соблюдением сносок, условий работы $\gamma_c$ (п. 6.14) и расчетных формул сетчатого армирования по п. 7.31 и 6.22.

**Tech Stack:** Python 3.13, NumPy, Matplotlib, ipywidgets, pytest, nbconvert, Docker/JupyterLab/nbviewer.

## Global Constraints
- Точные числовые совпадения с таблицами СП 15.13330.2020 (с Изм. № 1) без округлений табличных констант.
- Строгий учет сносок: тип раствора (жесткий цементный $\times 0{,}85$, органические пластификаторы $\times 0{,}9$), подготовка образцов ($\times 0{,}9$), пустотность (28–42% $\times 0{,}8$; 43–48% с четырьмя ярусами: $0{,}75$ для $\ge \text{М100}$, $0{,}70$ для М50..М75, $0{,}65$ для М10..М25, $0{,}60$ для нулевой прочности и до 0.4 МПа).
- Для кладки из ячеистого бетона на клею: согласно сноске 1 к Таблице 6.3 расчетные сопротивления принимаются по экспериментальным данным (`experimental_R`). Коллизия с несуществующей «Таблицей 6.15 на клей» исключена; Таблица 6.15 — это исключительно таблица коэффициента $k$.
- Пункты сетчатого армирования: формула (7.23) п. 7.31 с коэффициентом $p$ ($2{,}0$ для пустотности $\le 20\%$, $1{,}5$ для $20..30\%$, $1{,}0$ для $> 30\%$), $\gamma_{cs}$ по Таблице 6.14 (п. 6.22), конструктивные пределы по пп. 9.81–9.83, ограничение $R_{sk} \le 2R$.
- Разделение в блокноте интерактивного виджета и прямой статической ячейки вывода, чтобы исключить зависание `nbconvert` на `ipywidgets.Output`.

---

### Task 1: Создание нормативных таблиц и базовой структуры `sp15_materials.py`

**Files:**
- Create: `C:\Users\palex\Documents\expert\materials\sp15_materials.py`

**Interfaces:**
- Produces:
  - Словари: `TABLE_6_1_BRICK`, `TABLE_6_2_CERAMIC_LARGE_BLOCKS`, `TABLE_6_3_AERATED_MORTAR`, `TABLE_6_4_CONCRETE_LARGE_BLOCKS`, `TABLE_6_5_CONCRETE_SOLID_STONES`, `TABLE_6_6_CONCRETE_HOLLOW_STONES`, `TABLE_6_7_VIBRO_BRICK`, `TABLE_6_8_NATURAL_STONES`, `TABLE_6_9_RUBBLE_STONE`, `TABLE_6_10_RUBBLE_CONCRETE`, `TABLE_6_11_TENSION_JOINTS`, `TABLE_6_12_TENSION_STONES`, `TABLE_6_13_RUBBLE_CONCRETE_TENSION`, `TABLE_6_14_GAMMA_CS`, `TABLE_6_15_K_COEFF`, `TABLE_6_16_ALPHA`, `TABLE_6_17_DEFORMATION`, `TABLE_6_18_FRICTION`.
  - Функции: `list_masonry_stone_types() -> List[str]`, `list_stone_grades(stone_type: str) -> List[str]`, `list_mortar_grades(stone_type: str) -> List[str]`.

- [ ] **Step 1: Перенос полных числовых матриц таблиц 6.1–6.18 в `sp15_materials.py` из `sp15_tables_data.json`**
- [ ] **Step 2: Проверка импорта словарей и вспомогательных функций списков марок через python CLI**

---

### Task 2: Реализация классов `Masonry`, `MeshReinforcement` и `ReinforcedMasonry`

**Files:**
- Modify: `C:\Users\palex\Documents\expert\materials\sp15_materials.py`

**Interfaces:**
- Produces:
  - `class Masonry`:
    - `__init__(stone_type, stone_grade, mortar_grade, mortar_type='cement_lime', area_m2=1.0, is_ground_wet=False, long_term_hardening=False, specimen_grinded=False, stone_hollow_percent=0.0, experimental_R=None, ...)`
    - Properties: `R_base`, `gamma_c`, `R`, `Ru`, `alpha`, `E0`, `E_strength`, `E_stiffness`, `Rt_joint`, `Rtb_joint`, `Rsq_joint`, `Rt_stone`, `Rtb_stone`, `Rsq_stone`, `Rtw_stone`.
    - Methods: `get_diagram(n_points=100)`, `with_mesh_reinforcement(...)`, `to_dict()`, `to_markdown()`.
  - `class ReinforcedMasonry`:
    - Properties: `masonry`, `mu`, `p_coeff`, `gamma_cs`, `Rsk`, `alpha_sk`, `E0_sk`.
    - Method: `to_markdown()`.
  - Function: `generate_masonry_code_snippet(masonry, reinforced_masonry=None) -> str`.

- [ ] **Step 1: Реализация расчета сжатия $R$ со всеми сносками и условиями работы $\gamma_c$ (п. 6.14а-к)**
- [ ] **Step 2: Реализация характеристик растяжения/среза (Таблицы 6.11, 6.12, 6.13)**
- [ ] **Step 3: Реализация упругих характеристик ($R_u = k R$ по Табл. 6.15, $\alpha$ по Табл. 6.16, $E_0$, $E_{strength}$, $E_{stiffness}$) и кривой $\sigma(\varepsilon)$ (п. 6.26)**
- [ ] **Step 4: Реализация класса `ReinforcedMasonry` по п. 7.31 ($p$-фактор, $\mu$, $\gamma_{cs}$, $R_{sk} \le 2R$)**
- [ ] **Step 5: Реализация генератора сниппетов и экспорта в Markdown**

---

### Task 3: Разработка полного набора unit-тестов `test_sp15_materials.py`

**Files:**
- Create: `C:\Users\palex\Documents\expert\materials\test_sp15_materials.py`

**Interfaces:**
- Consumes: `Masonry`, `ReinforcedMasonry`, `list_masonry_stone_types`, `generate_masonry_code_snippet` из `sp15_materials.py`.
- Produces: 8 тестовых сценариев со сверенными по ревью эталонными значениями.

- [ ] **Step 1: Написание теста `test_brick_table_6_1_exact()` (М150/М100 -> 2.2 МПа, М150/М50 -> 1.8 МПа, М100/М100 -> 1.8 МПа, М100/М25 -> 1.3 МПа)**
- [ ] **Step 2: Написание теста `test_brick_footnotes_and_gamma_c()` (жесткий раствор $\times 0{,}85$, простенок $\le 0.3 \text{ м}^2 \times 0{,}8$, пустотность 28–42% $\times 0{,}8$, пустотность 43–48% $\times 0{,}75$, нулевой раствор $\times 0{,}60$)**
- [ ] **Step 3: Написание теста `test_ceramic_large_blocks_table_6_2()` (М100/М100 -> 2.0 МПа, М75/М100 -> 1.6 МПа, раствор М25 $\times 0{,}8 = 1{,}28$ МПа, паз-гребень 0.9/0.7 МПа)**
- [ ] **Step 4: Написание теста `test_aerated_concrete_table_6_3()` (В2.5 на растворе М50 -> 1.0 МПа, на растворе М25 -> 0.95 МПа, на клею по экспериментальным данным -> 1.4 МПа)**
- [ ] **Step 5: Написание теста `test_rubble_and_rubble_concrete_tables_6_9_and_6_10()` (бут М100/М100 3 мес -> 0.75 МПа, 28 дн -> 0.60 МПа, постелистый -> 1.125 МПа, траншея враспор -> 0.95 МПа, засыпка пазух -> 0.85 МПа; бутобетон В7.5 с бутом М100 -> 2.2 МПа, вибрированный -> 2.53 МПа)**
- [ ] **Step 6: Написание теста `test_tension_and_shear_tables_6_11_and_6_12()` (раствор М50+ -> Rsq=0.16, Rt=0.08, Rtb=0.12; раствор М25 -> Rsq=0.11, Rt=0.05, Rtb=0.08; кирпич М150 по камню -> Rsq=0.80, Rt=0.20, Rtb=0.30)**
- [ ] **Step 7: Написание теста `test_mesh_reinforcement_clause_7_31()` ($p=2.0$, $\mu=0.3351\%$, $\gamma_{cs}=0.6$, $R_{sk}=3.87$ МПа $\le 2R$)**
- [ ] **Step 8: Написание теста `test_elastic_and_diagram()` ($\alpha=1000$, $k=2.0$, $R_u=4.4$ МПа, $E_0=4400$ МПа, $E_{strength}=2200$ МПа, $E_{stiffness}=3520$ МПа, кривая $\sigma-\varepsilon$)**
- [ ] **Step 9: Запуск `pytest -v test_sp15_materials.py` и подтверждение 100% прохождения**

---

### Task 4: Создание интерактивного блокнота `masonry_selector.ipynb`

**Files:**
- Create: `C:\Users\palex\Documents\expert\materials\create_masonry_nb.py`
- Produces: `C:\Users\palex\Documents\expert\materials\masonry_selector.ipynb`

- [ ] **Step 1: Написание генератора блокнота `create_masonry_nb.py`:**
  - Ячейка 1: Вводный Markdown с описанием норм СП 15.13330.2020.
  - Ячейка 2: Импорт библиотек и `sp15_materials`.
  - Ячейка 3: Интерактивная панель `ipywidgets` (выбор вида кладки, марки камня, раствора, площади, параметров сетки).
  - Ячейка 4: Прямой статический расчет и отрисовка графиков $\sigma - \varepsilon$ для кирпича М150 / раствора М100 с сетчатым армированием.
  - Ячейка 5: Сводные таблицы характеристик неармированной и армированной кладки в Markdown.
  - Ячейка 6: Готовый фрагмент кода для вставки в расчетный блокнот.
  - Ячейка 7: Практический пример расчета несущей способности кирпичного простенка $380 \times 640$ мм на внецентренное сжатие.
- [ ] **Step 2: Запуск `python create_masonry_nb.py` и генерация `masonry_selector.ipynb`**

---

### Task 5: Развертывание на сервере Tailscale (`debian-13-6`) и публикация на витрине

**Files:**
- Remote: `/home/palex/jupyter/notebooks/materials/sp15_materials.py`
- Remote: `/home/palex/jupyter/notebooks/materials/masonry_selector.ipynb`
- Remote: `/home/palex/jupyter/notebooks/materials/test_sp15_materials.py`
- Modify: `C:\Users\palex\Documents\expert\materials\README.md`

- [ ] **Step 1: Передача файлов на сервер `debian-13-6` через Tailscale SSH**
- [ ] **Step 2: Копирование `sp15_materials.py` в `/opt/conda/lib/python3.13/site-packages/` контейнера `jupyter_master`**
- [ ] **Step 3: Запуск pytest внутри контейнера (`docker exec -w /home/palex/work/materials jupyter_master pytest -v`)**
- [ ] **Step 4: Предварительное выполнение блокнота `jupyter nbconvert --to notebook --execute --inplace masonry_selector.ipynb` внутри контейнера**
- [ ] **Step 5: Синхронизация отрендеренного блокнота на локальный компьютер**
- [ ] **Step 6: Обновление `README.md` с описанием СП 15 и ссылками**
- [ ] **Step 7: Верификация доступности через `curl.exe` на `http://debian-13-6:8080/localfile/materials/masonry_selector.ipynb` (HTTP 200)**
