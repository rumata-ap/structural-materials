import numpy as np
import pytest

from sp16_materials import (
    BOLT_AREAS,
    TABLE_1_GAMMA_C,
    TABLE_B6_RP,
    StructuralSteel,
    SteelBolt,
    generate_steel_code_snippet,
    list_gamma_c_options,
    list_steel_grades,
)


def test_sp16_physical_constants_and_c235_source_row():
    steel = StructuralSteel('C235', profile_type='plates', thickness=3.0)

    assert steel.E == 206000.0
    assert steel.G == 79000.0
    assert steel.nu == 0.30
    assert steel.Ryn == 235.0
    assert steel.Run == 360.0
    assert steel.Ry_base == pytest.approx(230.0)
    assert steel.Ru_base == pytest.approx(350.0)


def test_sp16_gamma_m_branches_use_source_numerator_and_denominator():
    statistical = StructuralSteel('C235', profile_type='plates', thickness=3.0, statistical_control=True)
    nonstatistical = StructuralSteel('С235', profile_type='plates', thickness=3.0, statistical_control=False)

    assert statistical.Ry_base == pytest.approx(230.0)
    assert statistical.Ru_base == pytest.approx(350.0)
    assert nonstatistical.Ry_base == pytest.approx(225.0)
    assert nonstatistical.Ru_base == pytest.approx(345.0)


def test_sp16_shapes_do_not_fallback_to_plates():
    with pytest.raises(ValueError, match=r'В\.5'):
        StructuralSteel('С235', profile_type='shapes', thickness=8.0)


def test_sp16_shape_and_plate_thickness_boundaries_are_source_rows():
    shape = StructuralSteel('С255', profile_type='shapes', thickness=8.0)
    plate = StructuralSteel('С355', profile_type='plates', thickness=120.0)

    assert shape.Ryn == 255.0
    assert shape.Ry_base == pytest.approx(250.0)
    assert plate.Ryn == 295.0
    assert plate.Ry_base == pytest.approx(285.0)


def test_sp16_b6_uses_published_rounded_rows_without_interpolation():
    steel = StructuralSteel('С235', profile_type='plates', thickness=3.0)
    assert len(TABLE_B6_RP) == 16
    assert set(TABLE_B6_RP) == {
        360.0, 370.0, 380.0, 390.0, 400.0, 430.0, 440.0, 450.0,
        460.0, 470.0, 480.0, 490.0, 510.0, 540.0, 570.0, 590.0,
    }
    assert steel.Rp_base == pytest.approx(351.0)
    assert steel.Rlp_base == pytest.approx(176.0)
    assert steel.Rcd_base == pytest.approx(9.0)
    assert steel.Rp == pytest.approx(351.0)


def test_sp16_c690_design_resistances_and_b9_are_explicitly_unavailable():
    steel = StructuralSteel('С690', profile_type='plates', thickness=20.0)
    with pytest.raises(ValueError, match='Ry|Ru'):
        _ = steel.Ry
    with pytest.raises(ValueError, match=r'В\.9'):
        steel.get_diagram_points('OACDEF')


def test_sp16_table_1_gamma_c_catalog_excludes_085():
    values = [value for _, value in list_gamma_c_options()]

    assert values == [0.75, 0.80, 0.87, 0.90, 0.95, 1.05, 1.10, 1.15, 1.20]
    assert set(values) == set(TABLE_1_GAMMA_C.values())
    assert 0.85 not in values


def test_sp16_b9_is_grouped_by_grade_family_and_uses_ryn():
    steel = StructuralSteel('С355', profile_type='plates', thickness=12.0)
    points = steel.get_diagram_points('OACDEF')

    assert tuple(points) == ('O', 'A', 'C', 'D', 'E', 'F')
    assert points['O'] == pytest.approx((0.0, 0.0))
    assert points['A'][1] == pytest.approx(0.8 * steel.Ryn)
    assert points['C'][1] == pytest.approx(steel.Ryn)
    assert points['E'][1] == pytest.approx(1.415 * steel.Ryn)
    eps, sig = steel.get_diagram('OACDEF', n_points=120)
    assert sig.max() == pytest.approx(points['E'][1])
    assert eps[-1] == pytest.approx(points['F'][0])


def test_sp16_b9_signed_curve_mirrors_tension_and_compression():
    steel = StructuralSteel('С255', profile_type='plates', thickness=3.0)
    eps, sig = steel.get_diagram('OACD', n_points=100, signed=True)

    assert eps.min() < 0.0 < eps.max()
    assert sig.min() < 0.0 < sig.max()
    assert np.max(np.abs(sig)) == pytest.approx(steel.Ryn)


def test_sp16_bolt_areas_are_taken_from_g9_and_parenthetical_diameters_are_gated():
    assert BOLT_AREAS[20]['A'] == 314.0
    assert BOLT_AREAS[20]['Abn'] == 245.0
    assert set(BOLT_AREAS) == {16, 18, 20, 22, 24, 27, 30, 36, 42, 48}
    with pytest.raises(ValueError, match='M12|диаметр'):
        SteelBolt('8.8', diameter=12)
    with pytest.raises(ValueError, match='ВЛ|ОРУ|special'):
        SteelBolt('8.8', diameter=27)
    SteelBolt('8.8', diameter=27, special_support=True)


def test_sp16_bolt_capacities_apply_gamma_c_to_both_and_gamma_b_only_to_shear():
    bolt = SteelBolt('8.8', diameter=20, gamma_b=0.9, gamma_c=0.8)

    assert bolt.Rbs == 332.0
    assert bolt.Rbt == 451.0
    assert bolt.shear_capacity(1) == pytest.approx(332.0 * 314.0 * 0.9 * 0.8 / 1000.0)
    assert bolt.tension_capacity() == pytest.approx(451.0 * 245.0 * 0.8 / 1000.0)


def test_sp16_bolt_validation_and_class_58_tension_absence():
    with pytest.raises(ValueError, match='gamma_b'):
        SteelBolt('8.8', gamma_b=1.01)
    bolt = SteelBolt('5.8', diameter=16)
    assert bolt.Rbt is None
    assert bolt.tension_capacity() is None
    with pytest.raises(ValueError, match='плоск'):
        bolt.shear_capacity(0)


def test_sp16_code_snippet_contains_correct_bolt_api():
    steel = StructuralSteel('С255', thickness=12.0)
    bolt = SteelBolt('8.8', 20)
    code = generate_steel_code_snippet(steel, bolt)

    assert 'from sp16_materials import StructuralSteel, SteelBolt' in code
    assert "grade='С255'" in code
    assert 'gamma_c=' in code
    assert 'Rbs = bolt.Rbs' in code


def test_sp16_grade_catalogs_include_source_variants():
    assert 'С355-К' in list_steel_grades('plates')
    assert 'С355П' in list_steel_grades('plates')
    assert 'С690' in list_steel_grades('plates')
    assert 'С255Б-1' in list_steel_grades('beams_parallel')
    assert 'С440Б' in list_steel_grades('beams_parallel')
