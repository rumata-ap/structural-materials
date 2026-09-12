import numpy as np
import pytest

from sp15_materials import (
    Masonry,
    ReinforcedMasonry,
    generate_masonry_code_snippet,
    list_masonry_stone_types,
    list_mortar_grades,
    list_stone_grades,
)


def _brick(stone_grade="M150", mortar_grade="M100", **kwargs):
    return Masonry(
        stone_type="brick",
        stone_grade=stone_grade,
        mortar_grade=mortar_grade,
        **kwargs,
    )


def test_brick_table_6_1_exact():
    assert _brick("M150", "M100").R == pytest.approx(2.2)
    assert _brick("M150", "M50").R == pytest.approx(1.8)
    assert _brick("M100", "M100").R == pytest.approx(1.8)
    assert _brick("M100", "M25").R == pytest.approx(1.3)


def test_brick_footnotes_and_gamma_c():
    assert _brick("M150", "M50", mortar_type="rigid_cement").R == pytest.approx(1.53)
    assert _brick("M150", "M100", area_m2=0.3).R == pytest.approx(1.76)
    assert _brick("M150", "M100", stone_hollow_percent=35).R == pytest.approx(1.76)
    assert _brick("M150", "M100", stone_hollow_percent=45).R == pytest.approx(1.65)
    assert _brick("M150", "0", stone_hollow_percent=45).R == pytest.approx(0.48)


def test_ceramic_large_blocks_table_6_2():
    def block(grade, mortar, **kwargs):
        return Masonry(
            "ceramic_large_block", grade, mortar, **kwargs
        )

    assert block("M100", "M100").R == pytest.approx(2.0)
    assert block("M75", "M100").R == pytest.approx(1.6)
    assert block("M75", "M25").R == pytest.approx(1.28)
    assert block("M75", "M0", vertical_joint="tongue_groove").R == pytest.approx(0.9)
    assert block("M50", "M0", vertical_joint="tongue_groove").R == pytest.approx(0.7)


def test_aerated_concrete_table_6_3():
    def aerated(grade, mortar, **kwargs):
        return Masonry("aerated_concrete", grade, mortar, **kwargs)

    assert aerated("B2.5", "M50").R == pytest.approx(1.0)
    assert aerated("B2.5", "M25").R == pytest.approx(0.95)
    assert aerated("B3.5", "M100").R == pytest.approx(1.5)
    assert aerated("B2.5", "glue", mortar_type="glue", experimental_R=1.4).R == pytest.approx(1.4)


def test_rubble_and_rubble_concrete_tables_6_9_and_6_10():
    rubble = lambda **kwargs: Masonry("rubble_stone", "M100", "M100", **kwargs)

    assert rubble().R == pytest.approx(0.75)
    assert rubble(rubble_age_days=28).R == pytest.approx(0.60)
    assert rubble(rubble_type="bedded").R == pytest.approx(1.125)
    assert rubble(trench_backfill="trench").R == pytest.approx(0.95)
    assert rubble(trench_backfill="backfill").R == pytest.approx(0.85)

    rubble_concrete = Masonry("rubble_concrete", "M100", "B7.5")
    assert rubble_concrete.R == pytest.approx(2.2)
    assert Masonry("rubble_concrete", "M200", "B7.5").R == pytest.approx(2.5)
    assert Masonry("rubble_concrete", "M100", "B7.5", is_vibrated=True).R == pytest.approx(2.53)


def test_tension_and_shear_tables_6_11_and_6_12():
    joint = _brick("M150", "M50")
    assert joint.Rsq_joint == pytest.approx(0.16)
    assert joint.Rt_joint == pytest.approx(0.08)
    assert joint.Rtb_joint == pytest.approx(0.12)

    weaker_joint = _brick("M150", "M25")
    assert weaker_joint.Rsq_joint == pytest.approx(0.11)
    assert weaker_joint.Rt_joint == pytest.approx(0.05)
    assert weaker_joint.Rtb_joint == pytest.approx(0.08)

    hollow_joint = _brick("M150", "M50", stone_hollow_percent=35)
    assert hollow_joint.Rsq_joint == pytest.approx(0.20)

    stone = _brick("M150", "M50")
    assert stone.Rsq_stone == pytest.approx(0.80)
    assert stone.Rt_stone == pytest.approx(0.20)
    assert stone.Rtb_stone == pytest.approx(0.30)


def test_mesh_reinforcement_clause_7_31():
    masonry = _brick("M150", "M100")
    reinforced = masonry.with_mesh_reinforcement(
        wire_diameter_mm=4,
        mesh_step_c_mm=50,
        mesh_rows_spacing=2,
        row_height_mm=65,
        rebar_class="B500",
        Rs=415.0,
        brick_type="single",
    )
    assert isinstance(reinforced, ReinforcedMasonry)
    assert reinforced.p_coeff == pytest.approx(2.0)
    assert reinforced.mu == pytest.approx(0.3866, abs=1e-4)
    assert reinforced.gamma_cs == pytest.approx(0.6)
    assert reinforced.Rsk == pytest.approx(4.13, abs=0.01)
    assert reinforced.Rsk <= 2 * masonry.R
    assert reinforced.is_applicable is True
    assert reinforced.is_constructive_only is False

    constructive = masonry.with_mesh_reinforcement(4, 50, 6, 65)
    assert constructive.is_constructive_only is True
    assert constructive.Rsk == pytest.approx(masonry.R)

    non_applicable = masonry.with_mesh_reinforcement(
        4, 50, 2, 200, experimental_R=3.1
    )
    assert non_applicable.is_applicable is False
    assert non_applicable.Rsk == pytest.approx(3.1)

    invalid_diameter = masonry.with_mesh_reinforcement(2, 50, 2, 65)
    assert invalid_diameter.is_applicable is False
    assert invalid_diameter.Rsk is None
    invalid_stone_grade = _brick("M50", "M100").with_mesh_reinforcement(4, 50, 2, 65)
    assert invalid_stone_grade.is_applicable is False
    invalid_mortar_grade = _brick("M150", "M25").with_mesh_reinforcement(4, 50, 2, 65)
    assert invalid_mortar_grade.is_applicable is False


def test_elastic_and_diagram():
    masonry = _brick("M150", "M100")
    assert masonry.alpha == pytest.approx(1000.0)
    assert masonry.Ru == pytest.approx(4.4)
    assert masonry.E0 == pytest.approx(4400.0)
    assert masonry.E_strength == pytest.approx(2200.0)
    assert masonry.E_stiffness == pytest.approx(3520.0)

    eps, sigma = masonry.get_diagram(n_points=100)
    assert len(eps) == 100
    assert len(sigma) == 100
    assert eps[0] == pytest.approx(0.0)
    assert sigma[0] == pytest.approx(0.0)
    assert sigma[-1] == pytest.approx(masonry.Ru, rel=1e-3)

    assert "from sp15_materials import Masonry" in generate_masonry_code_snippet(masonry)


def test_catalog_listing_helpers():
    assert "brick" in list_masonry_stone_types()
    assert "M150" in list_stone_grades("brick")
    assert "M100" in list_mortar_grades("brick")
    assert "B2.5" in list_stone_grades("aerated_concrete")
