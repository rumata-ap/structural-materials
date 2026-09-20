#!/usr/bin/env python3
"""Build PEP 427 wheel and sdist for structural-materials with zero external dependencies."""

import os
import tarfile
import zipfile
import hashlib
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PACKAGE = ROOT / "structural_materials"
VERSION = "0.3.0"
NAME = "structural-materials"
MODULE_NAME = "structural_materials"


def sha256_b64(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def build_metadata() -> str:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    lines = [
        "Metadata-Version: 2.1",
        f"Name: {NAME}",
        f"Version: {VERSION}",
        "Summary: Расчет нормативных характеристик строительных материалов (СП 15, СП 16, СП 63, СП 64)",
        "Author-email: Aleksandr Ponomarev <palexxvlad@yandex.ru>",
        "License: MIT",
        "Project-URL: Homepage, https://github.com/rumata-ap/structural-materials",
        "Project-URL: Documentation, https://structural-materials.readthedocs.io/",
        "Project-URL: Repository, https://github.com/rumata-ap/structural-materials.git",
        "Project-URL: Issues, https://github.com/rumata-ap/structural-materials/issues",
        "Keywords: structural-engineering,materials,concrete,rebar,steel,masonry,wood,timber,glulam,lvl,sp63,sp16,sp15,sp64",
        "Classifier: Development Status :: 4 - Beta",
        "Classifier: Intended Audience :: Science/Research",
        "Classifier: Topic :: Scientific/Engineering",
        "Classifier: License :: OSI Approved :: MIT License",
        "Classifier: Programming Language :: Python :: 3",
        "Classifier: Programming Language :: Python :: 3.9",
        "Classifier: Programming Language :: Python :: 3.10",
        "Classifier: Programming Language :: Python :: 3.11",
        "Classifier: Programming Language :: Python :: 3.12",
        "Classifier: Programming Language :: Python :: 3.13",
        "Classifier: Operating System :: OS Independent",
        "Requires-Python: >=3.9",
        "Description-Content-Type: text/markdown",
        "Requires-Dist: numpy>=1.20",
        "Provides-Extra: notebooks",
        'Requires-Dist: matplotlib; extra == "notebooks"',
        'Requires-Dist: ipywidgets>=8.0; extra == "notebooks"',
        'Requires-Dist: IPython; extra == "notebooks"',
        "Provides-Extra: docs",
        'Requires-Dist: sphinx>=7.0; extra == "docs"',
        'Requires-Dist: furo>=2023.9.10; extra == "docs"',
        'Requires-Dist: myst-parser>=2.0.0; extra == "docs"',
        'Requires-Dist: sphinx-copybutton>=0.5.2; extra == "docs"',
        "",
        readme,
    ]
    return "\n".join(lines)


def build_wheel() -> Path:
    DIST.mkdir(exist_ok=True)
    dist_info = f"{MODULE_NAME}-{VERSION}.dist-info"
    wheel_filename = DIST / f"{MODULE_NAME}-{VERSION}-py3-none-any.whl"

    metadata_bytes = build_metadata().encode("utf-8")
    wheel_meta_bytes = b"Wheel-Version: 1.0\nGenerator: custom-build (1.0)\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
    license_bytes = (ROOT / "LICENSE").read_bytes()

    records = []

    with zipfile.ZipFile(wheel_filename, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Package files
        for root, _, files in os.walk(PACKAGE):
            for file in files:
                if file.endswith((".pyc", ".pyo")):
                    continue
                path = Path(root) / file
                rel = path.relative_to(ROOT)
                data = path.read_bytes()
                zf.writestr(str(rel), data)
                records.append(f"{rel},sha256={sha256_b64(data)},{len(data)}")

        # Dist-info files
        zf.writestr(f"{dist_info}/METADATA", metadata_bytes)
        records.append(f"{dist_info}/METADATA,sha256={sha256_b64(metadata_bytes)},{len(metadata_bytes)}")

        zf.writestr(f"{dist_info}/WHEEL", wheel_meta_bytes)
        records.append(f"{dist_info}/WHEEL,sha256={sha256_b64(wheel_meta_bytes)},{len(wheel_meta_bytes)}")

        zf.writestr(f"{dist_info}/licenses/LICENSE", license_bytes)
        records.append(f"{dist_info}/licenses/LICENSE,sha256={sha256_b64(license_bytes)},{len(license_bytes)}")

        # RECORD file
        record_path = f"{dist_info}/RECORD"
        record_content = "\n".join(records) + f"\n{record_path},,\n"
        zf.writestr(record_path, record_content.encode("utf-8"))

    print(f"Created wheel: {wheel_filename}")
    return wheel_filename


def build_sdist() -> Path:
    DIST.mkdir(exist_ok=True)
    tar_filename = DIST / f"{MODULE_NAME}-{VERSION}.tar.gz"
    prefix = f"{MODULE_NAME}-{VERSION}"

    with tarfile.open(tar_filename, "w:gz") as tar:
        # Add PKG-INFO
        pkg_info_bytes = build_metadata().encode("utf-8")
        ti = tarfile.TarInfo(name=f"{prefix}/PKG-INFO")
        ti.size = len(pkg_info_bytes)
        ti.mode = 0o644
        import io
        tar.addfile(ti, io.BytesIO(pkg_info_bytes))

        # Add root files
        for filename in ["pyproject.toml", "README.md", "LICENSE"]:
            p = ROOT / filename
            if p.exists():
                tar.add(p, arcname=f"{prefix}/{filename}")

        # Add package files
        for root, _, files in os.walk(PACKAGE):
            for file in files:
                if file.endswith((".pyc", ".pyo")):
                    continue
                p = Path(root) / file
                rel = p.relative_to(ROOT)
                tar.add(p, arcname=f"{prefix}/{rel}")

    print(f"Created sdist: {tar_filename}")
    return tar_filename


if __name__ == "__main__":
    build_wheel()
    build_sdist()
