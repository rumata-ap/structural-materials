import pytest

from sp64_materials import (
    Glulam,
    LVL,
    OSB3,
    Plywood,
    StrengthClassWood,
    Timber,
    WoodContext,
    generate_wood_code_snippet,
    list_glulam_classes,
    list_load_duration_modes,
    list_lvl_classes,
    list_service_classes,
    list_strength_classes,
    list_wood_species,
)


SOURCE_REVISION = "СП 64.13330.2017 (ред. от 28.12.2023, Изменения № 1–4)"


def test_sorted_timber_uses_table_3_row_1a_with_explicit_geometry_case():
    context = WoodContext(load_duration="А")
    wood = Timber(
        sort=2,
        species="pine",
        geometry_case="rectangular_edge_h_le_500",
        context=context,
    )

    assert wood.resistance("bending") == pytest.approx(19.5)
    assert wood.resistance("tension_parallel") == pytest.approx(10.5)
    assert wood.source_revision == SOURCE_REVISION


def test_sorted_timber_design_false_uses_table_v1_and_missing_cell_fails():
    wood = Timber(sort=2, species="pine", geometry_case="rectangular_edge_h_le_500")

    assert wood.resistance("bending", design=False) == pytest.approx(24.0)
    with pytest.raises(ValueError, match="растяжение.*сорт 3"):
        Timber(sort=3, species="pine", geometry_case="rectangular_edge_h_le_500").resistance(
            "tension_parallel", design=False
        )


def test_c24_uses_appendix_v3_values_and_does_not_reduce_modulus_by_gamma_m():
    wood = StrengthClassWood("C24", context=WoodContext(load_duration="А"))

    assert wood.resistance("bending", design=False) == pytest.approx(24.0)
    assert wood.E_mean_MPa == pytest.approx(11000.0)
    assert wood.E_05_MPa == pytest.approx(7400.0)
    assert wood.density_mean_kg_m3 == pytest.approx(420.0)
    assert wood.density_k_kg_m3 == pytest.approx(350.0)
    assert wood.resistance("bending") == pytest.approx(20.0)
    assert wood.E_II_MPa == pytest.approx(11000.0)


def test_k24_uses_appendix_v4_values():
    wood = Glulam("K24", context=WoodContext(load_duration="А"))

    assert wood.resistance("bending", design=False) == pytest.approx(24.0)
    assert wood.E_mean_MPa == pytest.approx(11500.0)
    assert wood.E_05_MPa == pytest.approx(9400.0)
    assert wood.resistance("compression_parallel", design=False) == pytest.approx(24.0)


def test_lvl_uses_tables_v2_v2a_and_7_without_gamma_m_division():
    material = LVL("1/K45", context=WoodContext(load_duration="А"))

    assert material.resistance("bending") == pytest.approx(39.0)
    assert material.resistance("bending", design=False) == pytest.approx(45.0)
    assert material.resistance("tension_parallel") == pytest.approx(31.0)
    assert material.E_mean_MPa == pytest.approx(12000.0)
    assert material.E_05_MPa is None


def test_fsf_and_osb3_expose_directional_properties():
    plywood = Plywood(
        kind="FSF_birch",
        thickness_mm=8,
        layers=7,
        direction="parallel",
        context=WoodContext(load_duration="А"),
    )
    osb = OSB3(direction="major", context=WoodContext(load_duration="А"))

    assert plywood.resistance("bending") == pytest.approx(24.0)
    assert plywood.E_mean_MPa == pytest.approx(9000.0)
    assert osb.resistance("bending") == pytest.approx(23.0)
    assert osb.E_mean_MPa == pytest.approx(3600.0)
    assert osb.density_for_weight_kg_m3 == pytest.approx(600.0)


def test_service_class_4b_is_an_open_interval():
    context = WoodContext(load_duration="А", service_class="4б")

    context.validate_environment(wood_moisture_pct=21.0, relative_humidity_pct=86.0)
    with pytest.raises(ValueError, match="более 20"):
        context.validate_environment(wood_moisture_pct=20.0, relative_humidity_pct=86.0)
    with pytest.raises(ValueError, match="более 85"):
        context.validate_environment(wood_moisture_pct=21.0, relative_humidity_pct=85.0)
    assert context.to_dict()["service_class_display"] == "4б: >20% / >85%"


def test_context_canonicalizes_cyrillic_aliases_and_is_immutable():
    context = WoodContext(load_duration="G", service_class="4b")

    assert context.load_duration == "Г"
    assert context.service_class == "4б"
    with pytest.raises(Exception, match="cannot assign|неизмен"):
        context.load_duration = "А"


def test_context_accepts_all_normative_service_classes_and_modes():
    for sc in list_service_classes():
        ctx = WoodContext(load_duration="А", service_class=sc)
        assert ctx.service_class in list_service_classes()
    for mode in list_load_duration_modes():
        ctx = WoodContext(load_duration=mode, service_class="2")
        assert ctx.load_duration == mode


def test_design_requires_an_explicit_load_duration_context():
    wood = StrengthClassWood("C24")

    assert wood.resistance("bending", design=False) == pytest.approx(24.0)
    with pytest.raises(ValueError, match="режим нагружения"):
        wood.resistance("bending")
    with pytest.raises(TypeError, match="load_duration"):
        WoodContext()


def test_temperature_and_service_life_factors_are_applied():
    context = WoodContext(
        load_duration="Г",
        service_class="3",
        temperature_c=50.0,
        service_life_years=100,
    )
    wood = Timber(
        sort=2,
        species="pine",
        geometry_case="rectangular_edge_h_le_500",
        context=context,
    )

    factors = wood.factors("bending")
    assert factors["m_v"] == pytest.approx(0.9)
    assert factors["m_dlt"] == pytest.approx(0.66)
    assert factors["m_t"] == pytest.approx(0.8)
    assert factors["m_service_life"] == pytest.approx(0.8)
    assert wood.resistance("bending") == pytest.approx(19.5 * 0.9 * 0.66 * 0.8 * 0.8)

    interpolated = WoodContext(load_duration="А", temperature_c=42.5)
    assert interpolated.temperature_factor == pytest.approx(0.9)


def test_cross_fiber_and_perpendicular_compression_special_factors_are_explicit():
    cross_fiber = StrengthClassWood("C24", context=WoodContext(load_duration="Г"))

    tension_factors = cross_fiber.factors("tension_perpendicular")
    assert tension_factors["m_dlt_cross_fiber"] == pytest.approx(0.9)
    assert tension_factors["m_sm"] == pytest.approx(1.0)

    compression_factors = cross_fiber.factors("compression_perpendicular")
    assert compression_factors["m_sm"] == pytest.approx(1.15)


def test_species_factors_distinguish_european_larch_and_other_larch():
    european = Timber(
        sort=2,
        species="larch_european",
        geometry_case="rectangular_edge_h_le_500",
        context=WoodContext(load_duration="А"),
    )
    other = Timber(
        sort=2,
        species="larch_other",
        geometry_case="rectangular_edge_h_le_500",
        context=WoodContext(load_duration="А"),
    )

    assert european.resistance("bending") == pytest.approx(19.5)
    assert other.resistance("bending") == pytest.approx(19.5 * 1.2)
    assert other.resistance("shear_parallel") == pytest.approx(2.4)


@pytest.mark.parametrize(
    "factory, message",
    [
        (lambda: StrengthClassWood("C60"), "класс C60"),
        (lambda: Glulam("K40"), "класс K40"),
        (lambda: LVL("4/K30"), "класс LVL"),
        (lambda: OSB3(direction="diagonal"), "направлени"),
        (lambda: Plywood(kind="FSF_birch", thickness_mm=6, layers=7), "7-слойн"),
        (
            lambda: Timber(sort=2, geometry_case="round_logs"),
            "геометрическ",
        ),
    ],
)
def test_unsupported_material_options_fail_explicitly(factory, message):
    with pytest.raises(ValueError, match=message):
        factory()


def test_catalog_lists_follow_normative_order():
    assert list_strength_classes() == ["C14", "C16", "C18", "C20", "C22", "C24", "C27", "C30", "C35", "C40", "C45", "C50"]
    assert list_glulam_classes() == ["K20", "K24", "K28", "K32", "K36"]
    assert list_lvl_classes() == ["1/K45", "2/K40", "3/K35"]
    assert list_service_classes() == ["1а", "1б", "2", "3", "4а", "4б"]
    assert list_load_duration_modes() == ["А", "Б", "В", "Г", "Д", "Е", "Ж", "И", "К", "Л", "М"]
    assert "larch_european" in list_wood_species()


def test_reports_are_auditable_and_generated_code_reconstructs_material():
    material = StrengthClassWood("C24", context=WoodContext(load_duration="Г"))
    data = material.to_dict()

    assert data["source_revision"] == SOURCE_REVISION
    assert data["base_resistances_MPa"]["bending"] == pytest.approx(24.0)
    assert data["resistances_MPa"]["bending"] is not None
    assert data["factors"]["m_dlt"] == pytest.approx(0.66)
    assert "C24" in material.to_markdown()
    assert "МПа" in material.to_html()

    namespace = {}
    exec(generate_wood_code_snippet(material), namespace)
    assert namespace["material"].to_dict() == material.to_dict()

