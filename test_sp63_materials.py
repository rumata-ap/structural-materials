import pytest
import numpy as np
from sp63_materials import Concrete, Rebar, generate_code_snippet, list_concrete_grades, list_rebar_grades

def test_concrete_b25():
    c_long = Concrete(grade='B25', humidity='40-75%', long_term=True)
    assert c_long.Rbn == 18.5
    assert c_long.Rbtn == 1.55
    assert c_long.Rb_base == 14.5
    assert c_long.Rbt_base == 1.05
    assert c_long.gamma_b1 == 0.90
    assert np.isclose(c_long.Rb, 14.5 * 0.9)
    assert np.isclose(c_long.Rbt, 1.05 * 0.9)
    assert c_long.Eb == 30000.0
    assert c_long.phi_b_cr == 2.5
    assert np.isclose(c_long.Eb_red, 30000.0 / 3.5, atol=0.2)
    assert c_long.eps_b0 == 0.0034
    assert c_long.eps_b2 == 0.0048

    # Short term
    c_short = Concrete(grade='B25', humidity='40-75%', long_term=False)
    assert c_short.gamma_b1 == 1.0
    assert c_short.Rb == 14.5
    assert c_short.Eb_red == 30000.0
    assert c_short.eps_b0 == 0.0020
    assert c_short.eps_b2 == 0.0035

def test_concrete_gamma_b3():
    # Vertical casting
    c_vert = Concrete(grade='B25', long_term=True, gamma_b3=0.85)
    assert np.isclose(c_vert.Rb, 14.5 * 0.9 * 0.85, atol=0.01)
    # Rbt does not include gamma_b3
    assert np.isclose(c_vert.Rbt, 1.05 * 0.9, atol=0.01)

def test_concrete_diagrams():
    c = Concrete('B25')
    for model in ['bilinear', 'trilinear', 'nonlinear']:
        eps, sig = c.get_diagram(model=model, state='compression', n_points=50)
        assert len(eps) == 50
        assert len(sig) == 50
        assert np.isclose(eps[0], 0.0)
        assert np.isclose(sig[0], 0.0)
        assert np.isclose(eps[-1], c.eps_b2)
        assert np.max(sig) <= c.Rb + 1e-4

def test_rebar_a500():
    r_long = Rebar('A500', long_term=True)
    assert r_long.Rsn == 500.0
    assert r_long.Rs == 435.0
    assert r_long.Rsc == 435.0
    assert r_long.Es == 200000.0
    assert np.isclose(r_long.eps_s0, 435.0 / 200000.0)
    assert r_long.eps_s2 == 0.025
    assert r_long.Rsw == 300.0

    r_short = Rebar('A500', long_term=False)
    assert r_short.Rsc == 400.0

def test_snippet_generation():
    c = Concrete('B30')
    r = Rebar('A500')
    snippet = generate_code_snippet(c, r)
    assert 'from sp63_materials import Concrete, Rebar' in snippet
    assert "grade='B30'" in snippet
    assert "grade='A500'" in snippet

def test_list_grades():
    c_grades = list_concrete_grades()
    assert 'B25' in c_grades
    assert 'B60' in c_grades
    r_grades = list_rebar_grades()
    assert 'A500' in r_grades
    assert 'A240' in r_grades

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
