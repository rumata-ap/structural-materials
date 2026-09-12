import numpy as np
import pytest

from sp63_materials import (
    Concrete,
    Rebar,
    generate_code_snippet,
    list_concrete_grades,
    list_rebar_grades,
)


def test_concrete_b25_preserves_existing_heavy_catalog():
    concrete = Concrete('B25', humidity='40-75%', long_term=True)

    assert concrete.Rbn == 18.5
    assert concrete.Rbtn == 1.55
    assert concrete.Rb_base == 14.5
    assert concrete.Rbt_base == 1.05
    assert concrete.gamma_b1 == 0.90
    assert concrete.Rb == pytest.approx(14.5 * 0.9)
    assert concrete.Rbt == pytest.approx(1.05 * 0.9)
    assert concrete.Eb == 30000.0
    assert concrete.phi_b_cr == 2.5
    assert concrete.Eb_red == pytest.approx(30000.0 / 3.5, abs=0.2)
    assert concrete.eps_b0 == 0.0034
    assert concrete.eps_b2 == 0.0048


def test_concrete_bilinear_uses_normative_transition_strains():
    short = Concrete('B25', long_term=False)
    long = Concrete('B25', humidity='40-75%', long_term=True)

    assert short.eps_b1_red == 0.0015
    assert short.eps_bt1_red == 0.00008
    assert long.eps_b1_red == pytest.approx(0.0028)
    assert long.eps_bt1_red == pytest.approx(0.00022)

    points = short.get_diagram_points('bilinear', 'compression')
    assert points['origin'] == pytest.approx((0.0, 0.0))
    assert points['plateau_start'] == pytest.approx((0.0015, short.Rb))
    assert points['plateau_end'] == pytest.approx((short.eps_b2, short.Rb))


def test_concrete_trilinear_has_transition_and_plateau_nodes():
    concrete = Concrete('B25', long_term=False)
    points = concrete.get_diagram_points('trilinear', 'compression')

    assert points['transition'] == pytest.approx((0.6 * concrete.Rb / concrete.Eb, 0.6 * concrete.Rb))
    assert points['plateau_start'][1] == pytest.approx(concrete.Rb)
    assert points['plateau_end'][0] == pytest.approx(concrete.eps_b2)


def test_concrete_appendix_g_uses_ser_strength_and_eta_cutoff():
    concrete = Concrete('B25', long_term=False)
    compression = concrete.get_diagram_points('nonlinear', 'compression', signed=True)
    tension = concrete.get_diagram_points('nonlinear', 'tension', signed=True)

    assert compression['origin'] == pytest.approx((0.0, 0.0))
    assert compression['peak'][1] == pytest.approx(-concrete.Rb_ser)
    assert compression['eta_085'][1] == pytest.approx(-0.85 * concrete.Rb_ser)
    assert tension['peak'][1] == pytest.approx(concrete.Rbt_ser)
    eps, sigma = concrete.get_diagram('nonlinear', 'compression', n_points=160, signed=True)
    assert np.min(sigma) == pytest.approx(-concrete.Rb_ser)
    assert eps[-1] == pytest.approx(compression['eta_085'][0])


def test_concrete_appendix_g_uses_g8_g7_and_g9_parameters():
    concrete = Concrete('B25', long_term=False)
    compression = concrete.get_diagram_points('nonlinear', 'compression', signed=True)
    tension = concrete.get_diagram_points('nonlinear', 'tension', signed=True)

    grade = 25.0
    numerator = 1.0 + 0.75 * grade / 60.0 + 0.2 / grade
    denominator = 0.12 + grade / 60.0 + 0.2 / grade
    expected_eps_peak = grade / concrete.Eb * numerator / denominator
    assert abs(compression['peak'][0]) == pytest.approx(expected_eps_peak)
    assert compression['eta_085'][0] < compression['peak'][0]
    assert abs(compression['eta_085'][0]) < 0.01

    nu_bt_hat = 0.6 + 0.15 * concrete.Rbtn / 2.5
    expected_tension_peak = concrete.Rbt_ser / (concrete.Eb * nu_bt_hat)
    assert tension['peak'][0] == pytest.approx(expected_tension_peak)


def test_concrete_diagrams_keep_exact_endpoints_and_signed_convention():
    concrete = Concrete('B25', long_term=False)

    for model in ('bilinear', 'trilinear'):
        eps, sig = concrete.get_diagram(model=model, state='compression', n_points=50)
        points = concrete.get_diagram_points(model=model, state='compression')
        assert len(eps) == 50
        assert len(sig) == 50
        assert eps[0] == pytest.approx(points['origin'][0])
        assert sig[0] == pytest.approx(points['origin'][1])
        assert eps[-1] == pytest.approx(points['plateau_end'][0])

    eps_signed, sig_signed = concrete.get_diagram(
        model='bilinear', state='compression', n_points=50, signed=True
    )
    assert eps_signed[-1] < 0.0
    assert sig_signed[-1] < 0.0


def test_concrete_gamma_b3_does_not_reduce_tension():
    concrete = Concrete('B25', long_term=True, gamma_b3=0.85)

    assert concrete.Rb == pytest.approx(14.5 * 0.9 * 0.85)
    assert concrete.Rbt == pytest.approx(1.05 * 0.9)


def test_concrete_gamma_b5_applies_to_strength_and_deformation():
    concrete = Concrete('B25', long_term=False, gamma_b5=0.8)

    assert concrete.Rb == pytest.approx(14.5 * 0.8)
    assert concrete.eps_b2 == pytest.approx(0.0035 * 0.8)
    with pytest.raises(ValueError, match='gamma_b5'):
        Concrete('B25', gamma_b5=1.01)


def test_concrete_long_term_eps_b2_factor_is_applied_only_to_compression():
    concrete = Concrete('B80', humidity='40-75%', long_term=True)

    assert concrete.eps_b2 == pytest.approx(0.0048 * (270.0 - 80.0) / 210.0)
    assert concrete.eps_bt2 == pytest.approx(0.00031)


def test_concrete_requires_explicit_special_cellular_context():
    with pytest.raises(ValueError, match='density|плотност'):
        Concrete('B2.5', concrete_type='cellular')


def test_rebar_tables_and_aliases_are_complete():
    expected = {
        'Bp1200', 'Bp1300', 'Bp1400', 'Bp1500', 'Bp1600',
        'K1450', 'K1550', 'K1650', 'K1750', 'K1850', 'K1900',
    }
    assert expected.issubset(set(list_rebar_grades()))
    assert Rebar('Вр500').grade == 'Bp500'
    assert Rebar('К1750').Rsn == 1740.0
    assert Rebar('К1850').Rsn == 1840.0
    assert Rebar('К1900').Rs_base == 1670.0


def test_rebar_conditional_yield_and_trilinear_nodes():
    rebar = Rebar('A600', long_term=False)
    points = rebar.get_diagram_points(model='trilinear', state='tension')

    assert rebar.Es == 200000.0
    assert rebar.eps_s0 == pytest.approx(rebar.Rs / rebar.Es + 0.002)
    assert points['s1'] == pytest.approx((0.9 * rebar.Rs / rebar.Es, 0.9 * rebar.Rs))
    assert points['yield'] == pytest.approx((rebar.eps_s0, rebar.Rs))
    assert points['s2_limit'][0] == pytest.approx(2.0 * rebar.eps_s0 - points['s1'][0])
    assert points['s2_limit'][1] == pytest.approx(1.1 * rebar.Rs)
    assert points['plateau_end'] == pytest.approx((0.015, 1.1 * rebar.Rs))


def test_rebar_bilinear_physical_yield_and_signs():
    rebar = Rebar('A500', long_term=True)
    points = rebar.get_diagram_points(model='bilinear', state='tension')
    eps, sig = rebar.get_diagram(model='bilinear', state='compression', n_points=80, signed=True)

    assert rebar.Rsn == 500.0
    assert rebar.Rs == 435.0
    assert rebar.Rsc == 435.0
    assert rebar.Es == 200000.0
    assert rebar.eps_s0 == pytest.approx(rebar.Rs / rebar.Es)
    assert points['yield'] == pytest.approx((rebar.eps_s0, rebar.Rs))
    assert points['plateau_end'][0] == pytest.approx(0.025)
    assert eps[-1] < 0.0
    assert sig[-1] < 0.0


def test_rebar_model_auto_rejects_unmapped_high_strength_row():
    with pytest.raises(ValueError, match='automatic|auto|модел'):
        Rebar('K1750').get_diagram(model='auto')


def test_rebar_rsw_catalog_has_no_neighbor_fallback():
    assert Rebar('A240').Rsw == 170.0
    assert Rebar('A400').Rsw == 280.0
    assert Rebar('A500').Rsw == 300.0
    assert Rebar('B500').Rsw == 300.0
    assert Rebar('A600').Rsw is None
    assert Rebar('Bp1200').Rsw is None


def test_material_validation_rejects_invalid_diagram_inputs():
    concrete = Concrete('B25')
    rebar = Rebar('A500')

    with pytest.raises(ValueError, match='n_points'):
        concrete.get_diagram(n_points=0)
    with pytest.raises(ValueError, match='state'):
        concrete.get_diagram(state='unknown')
    with pytest.raises(ValueError, match='model'):
        rebar.get_diagram(model='unknown')


def test_snippet_generation():
    concrete = Concrete('B30')
    rebar = Rebar('A500')
    snippet = generate_code_snippet(concrete, rebar)

    assert 'from sp63_materials import Concrete, Rebar' in snippet
    assert "grade='B30'" in snippet
    assert "grade='A500'" in snippet


def test_list_grades():
    concrete_grades = list_concrete_grades()
    assert 'B25' in concrete_grades
    assert 'B60' in concrete_grades
    assert 'B1.5' in concrete_grades
    assert 'A500' in list_rebar_grades()
    assert 'A240' in list_rebar_grades()
