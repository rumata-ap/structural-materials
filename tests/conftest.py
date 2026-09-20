import sys
from pathlib import Path

# Добавляем корень репозитория, директорию пакета и scripts в sys.path
_repo_root = Path(__file__).resolve().parent.parent
_pkg_dir = _repo_root / "structural_materials"
_scripts_dir = _repo_root / "scripts"

for _p in [_repo_root, _pkg_dir, _scripts_dir]:
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

import structural_materials  # noqa: F401
