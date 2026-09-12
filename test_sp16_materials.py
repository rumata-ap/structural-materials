import pytest
import numpy as np
from sp16_materials import StructuralSteel, SteelBolt, list_steel_grades, generate_steel_code_snippet

def test_shapes_c255():
    # t = 8 mm (диапазон 4..10 мм)
    s1 = StructuralSteel('С255', profile_type='shapes', thickness=8.0, statistical_control=True)
    assert s1.Ryn == 255.0
    assert s1.Run == 380.0
    assert s1.Ry == 250.0
    assert s1.Ru == 370.0
    assert np.isclose(s1.Rs, 0.58 * 250.0)

    # Без статконтроля (знаменатель)
    s1_non = StructuralSteel('С255', profile_type='shapes', thickness=8.0, statistical_control=False)
    assert s1_non.Ry == 245.0
    assert s1_non.Ru == 360.0

    # t = 16 mm (диапазон 10..20 мм)
    s2 = StructuralSteel('С255', profile_type='shapes', thickness=16.0, statistical_control=True)
    assert s2.Ry == 240.0
    assert s2.Ru == 360.0

    # t = 30 mm (диапазон 20..40 мм)
    s3 = StructuralSteel('С255', profile_type='shapes', thickness=30.0, statistical_control=True)
    assert s3.Ry == 230.0

def test_shapes_c345_gamma_c():
    # Проверка коэффициента условий работы gamma_c = 0.95 (например, колонна жилого здания)
    s = StructuralSteel('С345', profile_type='shapes', thickness=8.0, gamma_c=0.95)
    assert s.Ry_base == 340.0
    assert s.Ry == round(340.0 * 0.95, 1)
    assert s.Ru == round(470.0 * 0.95, 1)
    assert s.Rs == round(0.58 * s.Ry, 1)

def test_plates_c355_thickness_brackets():
    # Проверка градаций толщин для листовой стали С355
    # 8..16 мм -> Ry=350/340
    p1 = StructuralSteel('С355', profile_type='plates', thickness=12.0)
    assert p1.Ry == 350.0

    # 16..40 мм -> Ry=340/330
    p2 = StructuralSteel('С355', profile_type='plates', thickness=25.0)
    assert p2.Ry == 340.0

    # 40..60 мм -> Ry=330/320
    p3 = StructuralSteel('С355', profile_type='plates', thickness=50.0)
    assert p3.Ry == 330.0

    # 60..80 мм -> Ry=320/310
    p4 = StructuralSteel('С355', profile_type='plates', thickness=70.0)
    assert p4.Ry == 320.0

    # 80..100 мм -> Ry=310/300
    p5 = StructuralSteel('С355', profile_type='plates', thickness=90.0)
    assert p5.Ry == 310.0

    # 100..160 мм -> Ry=285/280
    p6 = StructuralSteel('С355', profile_type='plates', thickness=120.0)
    assert p6.Ry == 285.0

def test_parallel_beams_c255b():
    # Двутавры с параллельными гранями полок по ГОСТ Р 57837
    b = StructuralSteel('С255Б', profile_type='beams_parallel', thickness=15.0)
    assert b.Ry == 240.0
    assert b.Ru == 360.0

def test_steel_diagram():
    s = StructuralSteel('С255', thickness=10.0)
    eps, sig = s.get_diagram(model='prandtl', n_points=50)
    assert len(eps) == 50
    assert len(sig) == 50
    assert np.isclose(eps[0], 0.0)
    assert np.isclose(sig[0], 0.0)
    assert np.isclose(np.max(sig), s.Ry)

def test_bolts():
    # Болт 8.8 М20
    bolt = SteelBolt(grade='8.8', diameter=20, gamma_b=0.9)
    assert bolt.Rbs == 332.0
    assert bolt.Rbt == 451.0
    assert bolt.A == 314.2
    assert bolt.Abn == 245.0
    # Nbs = 332 * 314.2 * 0.9 / 1000 = 93.88 кН
    assert np.isclose(bolt.shear_capacity(1), 332.0 * 314.2 * 0.9 / 1000.0, atol=0.1)

    # Болт 5.8 (не применяется на растяжение)
    b58 = SteelBolt(grade='5.8', diameter=16)
    assert b58.Rbt is None
    assert b58.tension_capacity() is None

def test_snippet_generation():
    steel = StructuralSteel('С255', thickness=12.0)
    bolt = SteelBolt('8.8', 20)
    code = generate_steel_code_snippet(steel, bolt)
    assert 'from sp16_materials import StructuralSteel, SteelBolt' in code
    assert 'grade=\'С255\'' in code
    assert 'Rbs = bolt.Rbs' in code

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
