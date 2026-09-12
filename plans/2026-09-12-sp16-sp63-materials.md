# СП 16/СП 63 и диаграммы материалов — план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Исправить нормативные данные, API выбора материалов, диаграммы и два интерактивных блокнота по СП 16.13330.2017 и СП 63.13330.2018 с регрессионными тестами и визуальной проверкой.

**Architecture:** Сохранить два самостоятельных Python-модуля `sp16_materials.py` и `sp63_materials.py`. Нормативные таблицы остаются локальными неизменяемыми каталогами внутри модулей, а расчётные классы только выбирают строку, применяют явно заданные коэффициенты и строят диаграммы по отдельным узловым данным. Генераторы `create_nb.py` и `create_steel_nb.py` остаются единственными источниками структуры блокнотов; сгенерированные `.ipynb` проверяются как артефакты.

**Tech Stack:** Python 3.13, NumPy, Matplotlib, ipywidgets, pytest, Jupyter nbconvert, JSON для генераторов блокнотов.

## Global Constraints

- Единственный нормативный профиль этой работы — два переданных HTML-файла: `C:\Users\palex\Documents\expert\norms\СП 16.13330.2017 Стальные конструкции.html` и `C:\Users\palex\Documents\expert\norms\СП 63.13330.2018. Свод правил. Бетонные и железобетонные конструкции. Основные положения.html`.
- Markdown-выгрузки норм не смешивать с HTML-профилем; поддержку иной редакции оформлять отдельным профилем.
- GreenSectionPy и OpenCS использовать только для сверки алгоритмов и знаков; runtime-зависимость от них не добавлять.
- Числа таблиц В.3–В.6, Г.5, Г.9, 6.7–6.15 переносить с сохранением числителей, знаменателей, знаков `-` и границ интервалов.
- `gamma_b5` СП 63 — внешний коэффициент по 6.1.12 и 6.1.27, default `1.0`, допустимый диапазон `0 < gamma_b5 <= 1.0`; он учитывается для характеристик прочности и деформаций.
- Для СП 16 `E=206000` МПа, `G=79000` МПа, `nu=0.30`; для СП 63 `Es=1.95e5` МПа у K и `Es=2.0e5` МПа у A/B.
- Молчаливые fallback к соседней марке, B60, соседней группе В.9 или интерполяции В.6 запрещены.
- Существующие изменения, относящиеся к СП 15, не изменять, не индексировать и не включать в коммиты этой работы.
- Каждый функциональный блок реализовать через TDD: сначала failing-тест, затем минимальная реализация, затем целевой тест и полный `pytest`.

## Карта файлов

- Modify: `sp63_materials.py` — каталоги СП 63, классы `Concrete`/`Rebar`, узловые данные и диаграммы.
- Modify: `test_sp63_materials.py` — нормативные и геометрические регрессии СП 63.
- Modify: `sp16_materials.py` — каталоги СП 16, `StructuralSteel`, `SteelBolt`, варианты В.1 и расчёт сопротивлений.
- Modify: `test_sp16_materials.py` — регрессии таблиц В.3–В.6, В.9, Г.5/Г.9 и формул 14.2.9.
- Modify: `create_nb.py` — генератор блокнота `material_selector.ipynb`.
- Modify: `create_steel_nb.py` — генератор блокнота `steel_selector.ipynb`.
- Regenerate: `material_selector.ipynb`, `steel_selector.ipynb`.
- Create: `test_notebook_generators.py` — компиляция генераторов, проверка JSON и состава исполняемых ячеек.
- Modify: `README.md` — актуальные API, источник редакции и локальная команда выполнения.
- Do not modify: `plans/2026-09-12-sp15-materials.md`, `specs/2026-09-12-sp15-materials-design.md` и внешние проекты.

---

### Task 1: Зафиксировать failing-регрессии и API узлов диаграмм

**Files:**
- Modify: `test_sp63_materials.py`
- Modify: `test_sp16_materials.py`
- Create: `test_notebook_generators.py`

**Interfaces:**
- Tests consume the current public constructors and the planned public methods:
  `Concrete.get_diagram(model='bilinear', state='compression', n_points=100, signed=False)`,
  `Concrete.get_diagram_points(model='bilinear', state='compression', signed=False)`,
  `Rebar.get_diagram(model='auto', state='tension', n_points=100, signed=False)`,
  `Rebar.get_diagram_points(model='auto', state='tension', signed=False)`,
  `StructuralSteel.get_diagram(model='OACD', n_points=100, eps_max=None, signed=False)`,
  `StructuralSteel.get_diagram_points(model='OACD', signed=False)`,
  `SteelBolt(grade='8.8', diameter=20, gamma_b=1.0, gamma_c=1.0, special_support=False)`.
- The point methods return `Dict[str, Tuple[float, float]]` with this exact key contract:
  - concrete bilinear: `origin`, `plateau_start`, `plateau_end`;
  - concrete trilinear: `origin`, `transition`, `plateau_start`, `plateau_end`;
  - concrete Appendix G compression: `origin`, `peak`, `eta_085`; concrete Appendix G tension: `origin`, `peak`, `failure`;
  - rebar bilinear: `origin`, `yield`, `plateau_end`; rebar trilinear: `origin`, `s1`, `yield`, `s2_limit`, `plateau_end`;
  - steel B.1: only the selected uppercase source labels from `O`, `A`, `B`, `C`, `D`, `E`, `F`.
  The tuple is always `(epsilon, sigma)` in the selected sign convention. `plateau_end` is the last normative point, not an implicit hardcoded strain.
- Public scalar properties used by tests are `Concrete.eps_b1_red`, `Concrete.eps_bt1_red`,
  `StructuralSteel.Rlp_base`, `StructuralSteel.Rcd_base`, `Rebar.eps_s0`, and
  `Rebar.eps_s2`; each is part of the contract and must appear in `to_dict()` where
  it is meaningful.

- [ ] **Step 1: Replace stale assertions that encode known defects.**

  Add tests with exact assertions for the following cases:

  ```python
  def test_sp63_bilinear_uses_normative_transition_strain():
      concrete = Concrete('B25', long_term=False)
      assert concrete.eps_b1_red == 0.0015
      points = concrete.get_diagram_points('bilinear', 'compression')
      assert points['plateau_start'] == pytest.approx((0.0015, concrete.Rb))
      assert points['plateau_end'][0] == pytest.approx(concrete.eps_b2)

  def test_sp63_conditional_rebar_and_trilinear_nodes():
      rebar = Rebar('A600', long_term=False)
      assert rebar.Es == 200000.0
      assert rebar.eps_s0 == pytest.approx(rebar.Rs / rebar.Es + 0.002)
      points = rebar.get_diagram_points(model='trilinear', state='tension')
      assert points['s1'] == pytest.approx((0.9 * rebar.Rs / rebar.Es, 0.9 * rebar.Rs))
      assert points['yield'] == pytest.approx((rebar.eps_s0, rebar.Rs))
      assert points['s2_limit'][1] == pytest.approx(1.1 * rebar.Rs)
      assert points['plateau_end'][0] == pytest.approx(0.015)

  def test_sp16_constants_and_b6_are_exact():
      steel = StructuralSteel('С235', profile_type='plates', thickness=3.0)
      assert steel.E == 206000.0
      assert steel.G == 79000.0
      assert steel.Ry_base == pytest.approx(230.0)
      assert steel.Ru_base == pytest.approx(350.0)
      assert steel.Rp_base == pytest.approx(351.0)
      assert steel.Rlp_base == pytest.approx(176.0)
      assert steel.Rcd_base == pytest.approx(9.0)

  def test_sp16_no_cross_table_or_b9_fallback():
      with pytest.raises(ValueError, match='В.5'):
          StructuralSteel('С235', profile_type='shapes', thickness=8.0)
      with pytest.raises(ValueError, match='В.9'):
          StructuralSteel('С690', profile_type='plates', thickness=20.0).get_diagram()

  def test_bolt_capacities_apply_gamma_c_to_both_and_gamma_b_only_to_shear():
      bolt = SteelBolt('8.8', diameter=20, gamma_b=0.9, gamma_c=0.8)
      assert bolt.shear_capacity(1) == pytest.approx(332.0 * 314.0 * 0.9 * 0.8 / 1000.0)
      assert bolt.tension_capacity() == pytest.approx(451.0 * 245.0 * 0.8 / 1000.0)

  def test_sp63_appendix_g_peak_cutoff_and_signs():
      concrete = Concrete('B25', long_term=False)
      compression = concrete.get_diagram_points('nonlinear', 'compression', signed=True)
      tension = concrete.get_diagram_points('nonlinear', 'tension', signed=True)
      assert compression['peak'][1] == pytest.approx(-concrete.Rb_ser)
      assert compression['eta_085'][1] == pytest.approx(-0.85 * concrete.Rb_ser)
      assert tension['peak'][1] == pytest.approx(concrete.Rbt_ser)
      eps_c, sig_c = concrete.get_diagram('nonlinear', 'compression', n_points=160, signed=True)
      assert np.min(sig_c) == pytest.approx(-concrete.Rb_ser)
      assert eps_c[-1] == pytest.approx(compression['eta_085'][0])

  def test_sp63_rsw_catalog_and_long_term_eps_b2_factor():
      assert Rebar('A240').Rsw == 170.0
      assert Rebar('A400').Rsw == 280.0
      assert Rebar('A500').Rsw == 300.0
      assert Rebar('B500').Rsw == 300.0
      assert Rebar('A600').Rsw is None
      concrete = Concrete('B80', humidity='40-75%', long_term=True)
      assert concrete.eps_b2 == pytest.approx(0.0048 * (270.0 - 80.0) / 210.0)

  def test_sp16_b9_uses_source_family_and_ryn():
      steel = StructuralSteel('С355', profile_type='plates', thickness=12.0)
      points = steel.get_diagram_points('OACDEF')
      assert tuple(points) == ('O', 'A', 'C', 'D', 'E', 'F')
      assert points['O'] == pytest.approx((0.0, 0.0))
      assert points['A'][1] == pytest.approx(0.8 * steel.Ryn)
      assert steel.get_diagram('OACDEF', n_points=120)[1].max() == pytest.approx(1.0 * steel.Ryn)
  ```

  Add exact table-row checks for Bp1200–Bp1600, K1450/K1550/K1650/K1750/K1850/K1900, C355-K, C355P, C440B and the special B3/B5 thickness intervals. Use source values with the numerator/denominator of `gamma_m`, not rounded markdown values. Replace the existing `test_concrete_diagrams` assertion that every model ends at `c.eps_b2` with a model-specific assertion: bilinear/trilinear end at their `plateau_end`, while Appendix G compression ends at `eta_085`; replace `test_steel_diagram`'s `model='prandtl'`/`max == Ry` assertion with explicit `OACD` point and source-normalized stress assertions; update `test_bolts` from `A == 314.2` to `A == 314.0`; recheck `test_shapes_*` and `test_plates_c355_thickness_brackets` against the selected HTML numerator/denominator rows.

- [ ] **Step 2: Add explicit negative tests for input validation.**

  Cover `n_points <= 0`, unknown `state`/`model`, `gamma_b5 > 1`, `gamma_b > 1`, zero shear planes, M12, parenthetical bolt diameters without `special_support=True`, light/cellular missing density or humidity, and B9 classes without a source curve.

- [ ] **Step 3: Add notebook generator smoke tests.**

  The generator contract is `create_notebook(output_path: Path | None = None) -> Path` and `create_steel_notebook(output_path: Path | None = None) -> Path`. With `output_path=None`, each function writes beside its own `.py` file via `Path(__file__).resolve().parent`; with a path, it writes exactly there and returns that `Path`. The test calls both functions with `tmp_path / 'material_selector.ipynb'` and `tmp_path / 'steel_selector.ipynb'`, loads each result with `json.load`, compiles every code cell with `compile(source, filename, 'exec')`, and asserts that the generated source contains `get_diagram_points`, `TABLE_1_GAMMA_C`, no M12 option, and an explicit `OACDEF` option.

- [ ] **Step 4: Run the focused tests and record the expected failures.**

  Run:

  ```powershell
  python -m pytest -q test_sp63_materials.py test_sp16_materials.py test_notebook_generators.py
  ```

  Expected result before implementation: failures on the known constants, missing table rows, incorrect diagrams, fallback behavior, bolt formulas and notebook source checks. No unrelated SP15 test or file may be changed.

- [ ] **Step 5: Commit only the test contract.**

  ```powershell
  git add -- test_sp63_materials.py test_sp16_materials.py test_notebook_generators.py
  git commit -m "test: specify SP16 SP63 material regressions"
  ```

---

### Task 2: Реализовать бетон СП 63 и приложение Г

**Files:**
- Modify: `sp63_materials.py: CONCRETE_GRADES, TABLE_6_7_RBN, TABLE_6_7_RBTN, TABLE_6_8_RB, TABLE_6_8_RBT, TABLE_6_10_DEFORMATIONS, TABLE_6_11_EB, TABLE_6_12_PHI_CR, Concrete`
- Test: `test_sp63_materials.py`

**Interfaces:**
- Preserve existing `Concrete(grade, concrete_type, humidity, long_term, gamma_b1, gamma_b2, gamma_b3, gamma_b4, gamma_b5)` calls.
- Add optional explicit context fields `density=None`, `curing=None`, `cellular_humidity_percent=None`, `is_tensioning=False` without changing the behavior of existing heavy-concrete calls.
- Implement `Concrete.get_diagram(model='bilinear', state='compression', n_points=100, signed=False) -> Tuple[np.ndarray, np.ndarray]` and `Concrete.get_diagram_points(model, state, signed=False) -> Dict[str, Tuple[float, float]]`.
- Expose `eps_b1_red` and `eps_bt1_red`; retain `Eb_red` for `Eb/(1+phi)` and do not use it to derive the transition strains.

- [ ] **Step 1: Replace the concrete catalogs with source-profile data.**

  Keep the exact heavy-concrete rows from tables 6.7, 6.8, 6.11, 6.12 and 6.10. Extend the schema so `TABLE_6_10_DEFORMATIONS` stores `eps_b0`, `eps_b2`, `eps_b1_red`, `eps_bt0`, `eps_bt2`, `eps_bt1_red` for each ambient-humidity row. Apply `(270-B)/210` to the long-term `eps_b2` values for the classes where note 2 to table 6.10 requires it; keep the short-term B70–B100 rule as a separate `eps_b2` rule and do not apply either factor to `eps_bt2`. Add catalogs for B1.5–B2.5 and the supported fine-grained, light, porous and cellular variants, including density/curing selectors.

- [ ] **Step 2: Write the minimal type and coefficient resolver.**

  Normalize `B25`, `b25` and `25` to the same canonical class, validate the type/grade/density/curing combination, and raise `ValueError` on unsupported combinations. Compute `gamma_b1` by load duration only where the selected type permits it, keep `gamma_b2`/`gamma_b3` explicit, apply `gamma_b1=0.85` for the applicable long-term cellular/porous context, and calculate cellular `gamma_b4` from `cellular_humidity_percent` at 10%/25% with linear interpolation between the normative bounds. Validate `gamma_b5` and apply it to strength and deformation properties. Do not infer freezing/thawing context.

- [ ] **Step 3: Implement light-concrete special rules without heavy fallback.**

  Apply the table multipliers `Rbt × 0.8` for fine-grained/light concrete, `Rbt × 0.7` for porous concrete relative to light concrete, `Rbt × 1.2` only when `is_tensioning=True`, `Eb × 0.89` for heat-treated fine-grained group A, `Eb × 0.8` for non-autoclaved cellular concrete, density interpolation where the HTML provides it, and `alpha = 0.56 + 0.006B` for the tensioning-concrete context. For light concrete implement the permitted `phi_b,cr × (rho/2200)^2` and deformation factor `max(0.7, 0.4 + 0.6*rho/2200)`. For cellular concrete without a special creep rule raise a descriptive `ValueError`; never return the B60 row.

- [ ] **Step 4: Implement the three concrete diagrams and signed output.**

  Use these exact rules:

  ```python
  E = self.Eb  # initial modulus Eb; never substitute Eb_red or Eb,tau here
  # bilinear compression/tension
  sigma = R * epsilon / epsilon_1_red if epsilon <= epsilon_1_red else R

  # trilinear; epsilon_0 and epsilon_2 are eps_b0/eps_b2 or eps_bt0/eps_bt2
  # selected by state, and the first slope uses the initial Eb
  (epsilon, sigma) = (0.0, 0.0), (0.6 * R / E, 0.6 * R), (epsilon_0, R), (epsilon_2, R)

  # Appendix G secant-branch point
  omega_2 = 1.0 - omega_1
  root = np.sqrt(max(0.0, 1.0 - omega_1 * eta - omega_2 * eta * eta))
  nu = nu_hat + (1.0 - nu_hat) * root                 # rising branch
  nu = nu_hat - (nu_0 - nu_hat) * root                 # descending branch
  epsilon = eta * sigma_hat / (E * nu)
  sigma = eta * sigma_hat
  ```

  For Appendix G use `sigma_hat_b=-Rb_ser`, `sigma_hat_bt=Rbt_ser`, `nu_hat_bt=0.5`, `epsilon_hat_bt=1`, explicit rising/descending `nu_0` and `omega_1`, and include the descending compression branch only for `eta >= 0.85`. Solve the implicit parameter equations numerically with a bounded scalar solver and insert origin, peak, and `eta=0.85` into the returned arrays. In `signed=True`, compression is negative in both arrays and tension is positive; `signed=False` retains positive magnitudes for compatibility.

- [ ] **Step 5: Add point metadata and update exports.**

  Return the exact model-specific point keys declared in Task 1: concrete bilinear
  (`origin`, `plateau_start`, `plateau_end`), concrete trilinear
  (`origin`, `transition`, `plateau_start`, `plateau_end`), Appendix G compression
  (`origin`, `peak`, `eta_085`) and Appendix G tension (`origin`, `peak`, `failure`).
  Add `eps_b1_red`/`eps_bt1_red`, type, density, curing and both humidity inputs to
  `to_dict`, Markdown, HTML and generated snippets. Ensure all accessors validate
  `n_points` and `state` before allocating arrays.

- [ ] **Step 6: Run the concrete-focused tests.**

  ```powershell
  python -m pytest -q test_sp63_materials.py -k "concrete or diagram"
  ```

  Expected result: all concrete coefficient, deformation, sign, point-presence, light-concrete and no-fallback tests pass.

- [ ] **Step 7: Commit the concrete implementation.**

  ```powershell
  git add -- sp63_materials.py test_sp63_materials.py
  git commit -m "feat: correct SP63 concrete data and diagrams"
  ```

---

### Task 3: Реализовать арматуру СП 63 по таблицам 6.13–6.15

**Files:**
- Modify: `sp63_materials.py: TABLE_6_13_RSN, TABLE_6_14_REBAR, TABLE_6_15_RSW, Rebar`
- Test: `test_sp63_materials.py`

**Interfaces:**
- Preserve `Rebar(grade, long_term, gamma_s)` and treat `gamma_s` as an additional explicit user factor applied after the already normative values from table 6.14.
- Add `Rebar.get_diagram(model='auto', state='tension', n_points=100, signed=False)` and `Rebar.get_diagram_points(model='auto', state='tension', signed=False)`.
- Expose `Rs_ser`, `Rs_base`, `Rs`, `Rsc`, `Rsw`, `Es`, `eps_s0`, `eps_s2`, `diagram_kind` and `is_conditional_yield`.

- [ ] **Step 1: Transfer all source-profile reinforcement rows.**

  Store exact `Rsn`, `Rs`, `Rsc_short`, `Rsc_long` rows for A240/A400/A500/A600/A800/A1000, B500, Bp500/Bp1200–Bp1600, K1400/K1450/K1500/K1550/K1650/K1750/K1850/K1900. Store K1750/K1850/K1900 as literal rows (`Rsn=1740/1840/1920`, `Rs=1515/1600/1670`, `Rsc=500 (400)`), not as recalculated values. Keep K1600 only in the explanatory 6.2.13 model map because it is absent from tables 6.13/6.14. Normalize Cyrillic `А`, `В`, `К` and aliases `Bp`/`Вр` to canonical keys.

- [ ] **Step 2: Implement normative Rsw availability.**

  Return values only for A240=170, A400=280, A500=300 and B500=300. Return `None` for every other class and validate the catalog so no result exceeds 300 MPa. Do not generate Rsw for Bp or K from another class.

- [ ] **Step 3: Implement model selection and exact nodes.**

  Use an explicit class map for `model='auto'`: bilinear for A240–A500 and B500;
  trilinear for A600–A1000, Bp1200–Bp1500, K1400, K1500 and the normative
  6.2.13 name K1600. Since K1600 is absent from tables 6.13/6.14, it produces no
  selectable row; table-present K1550 and K1650–K1900 remain available for exact
  resistance reporting but `auto` raises a descriptive error for them instead of
  deriving a model from the number.

  Implement the exact nodes:

  ```python
  eps_s0 = Rs / Es                         # physical yield
  eps_s0 = Rs / Es + 0.002                 # conditional yield
  bilinear: (0, 0) -> (eps_s0, Rs) -> (0.025, Rs)
  eps_s1 = 0.9 * Rs / Es
  eps_s2_limit = 2.0 * eps_s0 - eps_s1
  trilinear: (0, 0) -> (eps_s1, 0.9*Rs) -> (eps_s0, Rs)
              -> (eps_s2_limit, 1.1*Rs) -> (0.015, 1.1*Rs)
  ```

  On `eps_s1 <= eps <= eps_s0`, calculate exactly
  `sigma_s = ((1 - sigma_s1/Rs) * (eps_s-eps_s1)/(eps_s0-eps_s1) + sigma_s1/Rs) * Rs`;
  on the next segment use the same expression capped by `min(sigma_s, 1.1*Rs)`.
  Hold `1.1*Rs` through `eps_s2=0.015`, mirror both branches in `signed=True`,
  and return point keys `origin`, `s1`, `yield`, `s2_limit`, `plateau_end`.

- [ ] **Step 4: Update serialization and snippets.**

  Add `diagram_kind`, `is_conditional_yield`, model, `Es`, `eps_s0`, and `eps_s2` to `to_dict`, Markdown, HTML and code snippets. Keep `Rsw=None` visible as “Не применяется”, not as a neighboring value.

- [ ] **Step 5: Run and commit the reinforcement tests.**

  ```powershell
  python -m pytest -q test_sp63_materials.py -k "rebar or list_grades"
  git add -- sp63_materials.py test_sp63_materials.py
  git commit -m "feat: correct SP63 reinforcement tables and diagrams"
  ```

---

### Task 4: Исправить таблицы и диаграммы прокатной стали СП 16

**Files:**
- Modify: `sp16_materials.py: TABLE_B3_PLATES_TUBES, TABLE_B4_PARALLEL_BEAMS, TABLE_B5_SHAPES, TABLE_B6_RP, StructuralSteel`
- Modify: `test_sp16_materials.py`

**Interfaces:**
- Preserve `StructuralSteel(grade, profile_type, thickness, statistical_control, gamma_c)` and accept Latin/Cyrillic aliases for `C/С` and grade suffixes while exposing one canonical grade key.
- Add `TABLE_1_GAMMA_C` and `list_gamma_c_options() -> List[Tuple[str, float]]`.
- Implement `StructuralSteel.get_diagram(model='OACD', n_points=100, eps_max=None, signed=False)` and `get_diagram_points(model='OACD', signed=False)`.
- Expose `Ry_base`, `Ru_base`, `Ry`, `Ru`, `Ryn`, `Run`, `Rp_base`, `Rlp_base`, `Rcd_base`, `Rp`, `Rlp`, `Rcd`, `E`, `G`, `nu`, and `eps_y` without mixing numerator/denominator values.

- [ ] **Step 1: Replace B3/B4/B5 table literals from the selected HTML.**

  Add every supplied-HTML row and variant, including C355-K, C355P, C690, C255B-1, C345B-1, C355B-1, C440 and C440B. Store `t_min`, `t_max` (`None` for an open upper interval), inclusion flags, `Ryn`, `Run`, and separate numerator/denominator fields for `Ry` and `Ru`. Store `None` for source dashes, including C690 design resistances. Do not use B3 as a fallback for shapes or B4 as a fallback for another profile type.

- [ ] **Step 2: Implement exact interval selection and source profiles.**

  Resolve a row by the source inclusion flags, reject gaps and non-positive thickness, support B4 `>100` as an open interval, and expose an error containing the table name for an unavailable grade. Select `gamma_m=1.025` for statistical control and `gamma_m=1.050` otherwise; calculate only fields that have a source numerator/denominator. A missing C690 `Ry`/`Ru` must raise rather than use a neighboring row.

- [ ] **Step 3: Implement B6 using one canonical representation.**

  The public canonical values are the rounded values printed in the selected HTML
  table В.6: store all 16 exact `Run` rows `360, 370, 380, 390, 400, 430, 440,
  450, 460, 470, 480, 490, 510, 540, 570, 590` together with the source `Rp`, `Rlp`
  and `Rcd` values for both gamma-m contexts. For example, the Run=360 row exposes
  `Rp_base=351/343`, `Rlp_base=176/171`, `Rcd_base=9/9` for statistical/non-statistical
  control. The formulas `Rp=Run/gamma_m`, `Rlp=0.5*Run/gamma_m` and
  `Rcd=0.025*Run/gamma_m` are retained in comments/tests as the normative relation,
  but are not recomputed after the table's published rounding. Apply `gamma_c` only
  in the final properties. An unknown Run raises `ValueError` instead of interpolation.

- [ ] **Step 4: Implement table 1 and validation.**

  Populate `TABLE_1_GAMMA_C` with only the source values `0.75, 0.80, 0.87, 0.90, 0.95, 1.05, 1.10, 1.15, 1.20` and their exact labels. The API accepts a finite explicit value for compatibility, while the notebook uses only this catalog and never offers 0.85 or silently multiplies unrelated special coefficients.

- [ ] **Step 5: Implement B9 by grade family and Ryn normalization.**

  Store the exact B9 normalized points by source family, not by an `Ryn` threshold:

  ```python
  TABLE_B9_GROUPS = {
      1: ('С245', 'С255', 'С255Б', 'С255Б-1'),
      2: ('С345', 'С345К', 'С355', 'С355-1', 'С355П', 'С345Б', 'С345Б-1', 'С355Б', 'С355Б-1'),
      3: ('С390', 'С390-1', 'С390Б'),
      4: ('С440', 'С440Б'),
      5: ('С550', 'С590'),
  }
  sigma = sigma_bar * Ryn
  epsilon = epsilon_bar * (Ryn / E)
  ```

  Use exact normalized coordinates from the source for OBD, OACD and OACDEF. C690 is absent from B9 and must raise a table В.9 error. Do not scale normalized source coordinates by selected `Ry`; any design-resistance conversion remains a separately named operation.

- [ ] **Step 6: Implement diagram variants and signed arrays.**

  Map only `OBD`, `OACD`, `OACDEF` to source point sequences. Keep `prandtl` and `hardening` as compatibility aliases only when they map to an explicit source variant; make the API default explicit `OACD`, while the notebook selects `OACDEF` as a demonstration option. Compute `eps_max` from the selected source endpoint when it is omitted, insert all named points into the arrays, and mirror tension/compression for `signed=True`.

- [ ] **Step 7: Run and commit the structural-steel tests.**

  ```powershell
  python -m pytest -q test_sp16_materials.py -k "steel or diagram or table"
  git add -- sp16_materials.py test_sp16_materials.py
  git commit -m "feat: correct SP16 steel tables and B9 diagrams"
  ```

---

### Task 5: Исправить болты СП 16 и их расчётные отчёты

**Files:**
- Modify: `sp16_materials.py: TABLE_G5_BOLTS, BOLT_AREAS, SteelBolt`
- Modify: `test_sp16_materials.py`

**Interfaces:**
- Preserve `SteelBolt(grade='8.8', diameter=20, gamma_b=1.0)` and add `gamma_c=1.0`, `special_support=False`.
- Keep `shear_capacity(n_shear_planes=1) -> float` and `tension_capacity() -> Optional[float]`; add `gamma_c` to `to_dict`, Markdown, HTML and generated snippets.

- [ ] **Step 1: Replace the diameter catalog with Г.9.**

  Store 16, 18, 20, 22, 24, 27, 30, 36, 42 and 48 mm with the tabular gross/net
  areas from Г.9, converted from cm² to mm² without recomputing `pi*d*d/4`.
  For example, M20 is `A=314.0` mm² and `Abn=245.0` mm²; M16 is `201.0` and
  `157.0` mm². Mark 18, 22 and 27 as special-support-only; reject them unless
  `special_support=True`. Reject M12 and every diameter absent from Г.9.

- [ ] **Step 2: Validate bolt inputs.**

  Require `0 < gamma_b <= 1.0`, finite `gamma_c > 0`, and a positive integer `n_shear_planes`. Retain `Rbt=None` and `tension_capacity() is None` for class 5.8.

- [ ] **Step 3: Implement formulas 14.2.9 exactly.**

  ```python
  Nbs_kN = Rbs * A * n_shear_planes * gamma_b * gamma_c / 1000.0
  Nbt_kN = None if Rbt is None else Rbt * Abn * gamma_c / 1000.0
  ```

  `gamma_b` must not appear in the tension expression. Use the exact table Г.5 values and do not round before the final kN presentation.

- [ ] **Step 4: Run and commit the bolt tests.**

  ```powershell
  python -m pytest -q test_sp16_materials.py -k "bolt"
  git add -- sp16_materials.py test_sp16_materials.py
  git commit -m "fix: correct SP16 bolt capacities and diameters"
  ```

---

### Task 6: Пересобрать блокноты и исправить визуализацию

**Files:**
- Modify: `create_nb.py`
- Modify: `create_steel_nb.py`
- Regenerate: `material_selector.ipynb`
- Regenerate: `steel_selector.ipynb`
- Test: `test_notebook_generators.py`

**Interfaces:**
- Generators expose `create_notebook(output_path: Path | None = None) -> Path` and
  `create_steel_notebook(output_path: Path | None = None) -> Path`. They import only
  the public module APIs and produce valid nbformat 4 JSON. A default call writes
  beside the generator file; a supplied path is used without any absolute machine
  specific path.
- The SP 63 notebook uses concrete type, density/curing, ambient humidity, cellular humidity where required, load duration, gamma coefficients, rebar grade and `model='auto'` controls.
- The SP 16 notebook uses profile type, grade, numeric thickness, statistical control, `TABLE_1_GAMMA_C`, explicit B.1 variant, bolt grade, Г.9 diameter and special-support context.

- [ ] **Step 1: Rewrite the SP 63 plotting cell around point metadata.**

  Call `get_diagram(model=w_diag_model.value, state='compression', n_points=160, signed=True)` and `get_diagram_points(model=w_diag_model.value, state='compression', signed=True)` for markers. Iterate over the returned `(label, (epsilon, sigma))` pairs so the exact model-specific keys (`plateau_start`, `plateau_end`, `transition`, `peak`, `failure`, `eta_085`) are plotted without hardcoded substitutions. Plot strain consistently in ‰ on every axis, label compression as negative and tension as positive, set x-limits from the returned arrays, and do not draw `eps_b0` as the bilinear peak or reuse the compression model for tension.

- [ ] **Step 2: Rewrite the SP 63 controls and output.**

  Populate all dropdowns from module catalogs, separate ambient humidity from cellular humidity, show a validation message for missing density/special rules, show `Rsw=None` as unavailable, and include the exact model name and sign convention in the chart title. Keep a static example cell so nbconvert can execute the notebook without an interactive event.

- [ ] **Step 3: Rewrite the SP 16 controls and plotting cell.**

  Build gamma-c options from `TABLE_1_GAMMA_C`, update grade options on profile changes, use a numeric thickness widget that permits values beyond 80 mm, and display a message for B4 `>100`. Use explicit `OBD`/`OACD`/`OACDEF` selection, plot every B.1 node with labels, derive x-limits from the diagram endpoint, and never include M12. Bolt bars must use the same Г.9 diameter catalog and show missing tension capacity as an absent bar rather than zero.

- [ ] **Step 4: Generate and structurally validate both notebooks.**

  ```powershell
  python create_nb.py
  python create_steel_nb.py
  python -m pytest -q test_notebook_generators.py
  ```

  Expected result: both generated files parse as nbformat 4, every code cell compiles, and no stale invalid option remains.

- [ ] **Step 5: Commit generator and notebook changes.**

  ```powershell
  git add -- create_nb.py create_steel_nb.py material_selector.ipynb steel_selector.ipynb test_notebook_generators.py
  git commit -m "fix: rebuild SP16 SP63 material selector diagrams"
  ```

---

### Task 7: Полное выполнение, визуальная QA и документация

**Files:**
- Modify: `README.md`
- Verify: `sp63_materials.py`, `sp16_materials.py`, `test_sp63_materials.py`, `test_sp16_materials.py`, `material_selector.ipynb`, `steel_selector.ipynb`

**Interfaces:**
- Local execution uses the repository working directory and the installed Python/Jupyter dependencies; a remote `debian-13-6` Jupyter process is not required for this change.
- The final repository must retain the two unrelated dirty SP15 files exactly as found.

- [ ] **Step 1: Run syntax and the complete test suite.**

  ```powershell
  python -m compileall -q sp63_materials.py sp16_materials.py create_nb.py create_steel_nb.py test_sp63_materials.py test_sp16_materials.py test_notebook_generators.py
  python -m pytest -q
  ```

  Expected result: exit code 0, all tests pass, and no test imports a module from GreenSectionPy or OpenCS.

- [ ] **Step 2: Execute copies of both generated notebooks locally.**

  ```powershell
  $qaDir = Join-Path ([System.IO.Path]::GetTempPath()) 'expert-materials-notebook-qa'
  New-Item -ItemType Directory -Force -Path $qaDir | Out-Null
  python -m jupyter nbconvert --to notebook --execute --output-dir $qaDir material_selector.ipynb --ExecutePreprocessor.timeout=120 --ExecutePreprocessor.allow_errors=False
  python -m jupyter nbconvert --to notebook --execute --output-dir $qaDir steel_selector.ipynb --ExecutePreprocessor.timeout=120 --ExecutePreprocessor.allow_errors=False
  ```

  Expected result: both commands finish with exit code 0, the source notebooks remain unchanged, and each executed copy contains at least one Matplotlib output and the selected-material tables/snippet output.

- [ ] **Step 3: Render HTML and inspect the actual charts.**

  ```powershell
  python -m jupyter nbconvert --to html --output-dir $qaDir $qaDir\material_selector.ipynb
  python -m jupyter nbconvert --to html --output-dir $qaDir $qaDir\steel_selector.ipynb
  ```

  Inspect the rendered figures for exact endpoint visibility, readable non-overlapping annotations, consistent ‰ labels, negative signed compression, visible B.1/B.9 nodes, no clipped legend, no artificial 2.5% endpoint, and no zero bar falsely representing unavailable bolt tension resistance. Remove `$qaDir` after inspection; no QA files are project artifacts.

- [ ] **Step 4: Update README to match the final public behavior.**

  Document the selected HTML source profile, local commands, canonical aliases, concrete/rebar model names, B.1 variant names, B4 open interval, and the fact that the generated notebooks are the source-of-structure artifacts. Remove claims that contradict the final catalogs, such as M12 support, unconditional Prandtl diagrams, free gamma-c values or remote-only installation.

- [ ] **Step 5: Verify scope and commit documentation.**

  ```powershell
  git diff --check
  git status --short
  git diff --name-only origin/main..HEAD
  git add -- README.md
  git commit -m "docs: document corrected SP16 SP63 material selectors"
  ```

  Confirm that the final status still lists only the pre-existing SP15 modifications, if they remain uncommitted, and that no external norm, GreenSectionPy or OpenCS file was modified.

## Final acceptance criteria

1. All tests in `test_sp63_materials.py`, `test_sp16_materials.py` and `test_notebook_generators.py` pass.
2. Both notebooks regenerate from their generators, execute locally without exceptions and render visible chart outputs.
3. SP 63 concrete diagrams use normative transition strains, Appendix G peaks and `eta >= 0.85`; rebar diagrams use the exact 6.2.11–6.2.15 nodes and `Es` values.
4. SP 16 uses complete source-profile B3/B4/B5/B6 data, exact gamma-m branches, family-based B9 normalization by `Ryn`, explicit B.1 variants and no fallback for C690.
5. Bolt capacities use `gamma_b` only in shear and `gamma_c` in both formulas as prescribed; M12 is absent and parenthetical diameters are gated.
6. The generated visualizations show actual API nodes and factual axes/units rather than hardcoded or clipped points.
