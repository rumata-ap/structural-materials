import json
from pathlib import Path

from create_nb import create_notebook
from create_steel_nb import create_steel_notebook


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
