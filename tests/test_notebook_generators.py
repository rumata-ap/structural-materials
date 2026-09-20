import json
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
for _dir in [_repo_root / "scripts", _repo_root / "structural_materials", _repo_root]:
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

from create_nb import create_notebook
from create_steel_nb import create_steel_notebook
from create_masonry_nb import create_masonry_notebook


def _assert_generated_notebook(path: Path, required_tokens):
    assert path.exists()
    notebook = json.loads(path.read_text(encoding='utf-8'))
    assert notebook['nbformat'] == 4
    source = '\n'.join(
        ''.join(cell.get('source', []))
        for cell in notebook['cells']
        if cell['cell_type'] == 'code'
    )
    for index, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            compile(''.join(cell.get('source', [])), f'{path.name}:cell-{index}', 'exec')
    for token in required_tokens:
        assert token in source


def test_generators_write_to_requested_directory_without_machine_absolute_paths(tmp_path):
    concrete_path = tmp_path / 'material_selector.ipynb'
    steel_path = tmp_path / 'steel_selector.ipynb'

    assert create_notebook(concrete_path) == concrete_path
    assert create_steel_notebook(steel_path) == steel_path
    _assert_generated_notebook(
        concrete_path,
        ('get_diagram_points', 'model="nonlinear"', 'signed=True'),
    )
    _assert_generated_notebook(
        steel_path,
        ('get_diagram_points', 'TABLE_1_GAMMA_C', 'OACDEF'),
    )


def test_steel_notebook_does_not_offer_m12(tmp_path):
    path = tmp_path / 'steel_selector.ipynb'
    create_steel_notebook(path)
    source = path.read_text(encoding='utf-8')

    assert 'M12' not in source
    assert 'd_list = [12' not in source


def test_concrete_notebook_does_not_display_generated_code(tmp_path):
    path = tmp_path / 'material_selector.ipynb'
    create_notebook(path)
    source = path.read_text(encoding='utf-8')

    assert 'generate_code_snippet' not in source
    assert 'Готовый фрагмент кода' not in source
    assert 'display(HTML(concrete.to_html()))' in source
    assert 'display(HTML(rebar.to_html()))' in source
    assert 'display(Markdown(concrete.to_markdown()))' not in source
    assert 'display(Markdown(rebar.to_markdown()))' not in source


def test_steel_notebook_does_not_display_generated_code(tmp_path):
    path = tmp_path / 'steel_selector.ipynb'
    create_steel_notebook(path)
    source = path.read_text(encoding='utf-8')

    assert 'generate_steel_code_snippet' not in source
    assert 'Готовый фрагмент кода' not in source
    assert 'display(HTML(steel.to_html()))' in source
    assert 'display(HTML(bolt.to_html()))' in source
    assert 'display(Markdown(steel.to_markdown()))' not in source
    assert 'display(Markdown(bolt.to_markdown()))' not in source


def test_masonry_notebook_has_static_and_interactive_sections(tmp_path):
    path = tmp_path / 'masonry_selector.ipynb'
    assert create_masonry_notebook(path) == path
    notebook = json.loads(path.read_text(encoding='utf-8'))
    assert len(notebook['cells']) == 6
    assert notebook['nbformat'] == 4
    code_cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
    for index, cell in enumerate(code_cells):
        compile(''.join(cell['source']), f'masonry-cell-{index}', 'exec')
    source = '\n'.join(''.join(cell['source']) for cell in code_cells)
    assert 'ipywidgets' in source
    assert 'get_diagram' in source
    assert 'Rsk' in source
    assert '380' in source and '640' in source
    assert 'Output(' not in source


def test_masonry_notebook_uses_russian_normative_stone_type_labels(tmp_path):
    path = tmp_path / 'masonry_selector.ipynb'
    create_masonry_notebook(path)
    notebook = json.loads(path.read_text(encoding='utf-8'))
    source = '\n'.join(
        ''.join(cell.get('source', []))
        for cell in notebook['cells']
        if cell['cell_type'] == 'code'
    )
    assert 'Кирпич всех видов' in source
    assert 'Керамические крупноформатные камни' in source
    assert 'Ячеистобетонные блоки (автоклавного твердения)' in source
    assert 'options=["brick", "ceramic_large_block", "aerated_concrete"]' not in source


def test_masonry_notebook_uses_framed_responsive_control_box(tmp_path):
    path = tmp_path / 'masonry_selector.ipynb'
    create_masonry_notebook(path)
    notebook = json.loads(path.read_text(encoding='utf-8'))
    source = '\n'.join(
        ''.join(cell.get('source', []))
        for cell in notebook['cells']
        if cell['cell_type'] == 'code'
    )
    assert 'description_width = "190px"' in source
    assert 'control_layout' not in source
    assert 'control.layout = widgets.Layout(width="98%")' in source
    assert 'Площадь сечения A, м²:' in source
    assert 'Диаметр проволоки d, мм:' in source
    assert 'Шаг ячейки сетки c, мм:' in source
    assert 'Интервал между сетками, рядов кладки:' in source
    assert 'Сетчатое армирование кладки' in source
    assert 'masonry_box = widgets.VBox(' in source
    assert 'layout=widgets.Layout(border="1px solid #ddd", padding="10px")' in source
    assert 'display(masonry_box)' in source


def test_masonry_notebook_does_not_display_generated_code_snippet(tmp_path):
    path = tmp_path / 'masonry_selector.ipynb'
    create_masonry_notebook(path)
    notebook = json.loads(path.read_text(encoding='utf-8'))
    source = '\n'.join(
        ''.join(cell.get('source', []))
        for cell in notebook['cells']
        if cell['cell_type'] == 'code'
    )
    assert 'generate_masonry_code_snippet' not in source
    assert 'Готовый фрагмент кода' not in source


def test_wood_notebook_is_valid_and_compiles():
    wood_path = _repo_root / "notebooks" / "wood_selector.ipynb"
    assert wood_path.exists()
    notebook = json.loads(wood_path.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert len(code_cells) > 0
    for index, cell in enumerate(code_cells):
        compile("".join(cell.get("source", [])), f"wood-cell-{index}", "exec")
    source = "\n".join("".join(cell.get("source", [])) for cell in code_cells)
    assert "Timber" in source
    assert "Glulam" in source
    assert "WoodContext" in source

