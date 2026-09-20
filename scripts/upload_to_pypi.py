#!/usr/bin/env python3
"""Upload built packages in dist/ to PyPI using PyPI API Token."""

import os
import sys
import uuid
import hashlib
import zipfile
import tarfile
import email
import base64
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PYPI_URL = "https://upload.pypi.org/legacy/"
TEST_PYPI_URL = "https://test.pypi.org/legacy/"


def extract_metadata(file_path: Path) -> list[tuple[str, str]]:
    text = ""
    if file_path.name.endswith(".whl"):
        with zipfile.ZipFile(file_path) as zf:
            for name in zf.namelist():
                if name.endswith(".dist-info/METADATA"):
                    text = zf.read(name).decode("utf-8")
                    break
    else:
        with tarfile.open(file_path, "r:gz") as tf:
            for member in tf.getmembers():
                if member.name.endswith("/PKG-INFO"):
                    f = tf.extractfile(member)
                    if f:
                        text = f.read().decode("utf-8")
                    break

    msg = email.message_from_string(text)
    fields: list[tuple[str, str]] = [
        (":action", "file_upload"),
        ("protocol_version", "1"),
        ("metadata_version", msg.get("Metadata-Version", "2.1")),
        ("name", msg.get("Name", "structural-materials")),
        ("version", msg.get("Version", "0.2.0")),
        ("summary", msg.get("Summary", "")),
        ("description", msg.get_payload()),
        ("description_content_type", msg.get("Description-Content-Type", "text/markdown")),
        ("author_email", msg.get("Author-email", "")),
        ("license", msg.get("License", "MIT")),
        ("requires_python", msg.get("Requires-Python", ">=3.9")),
    ]

    for c in (msg.get_all("Classifier") or []):
        fields.append(("classifiers", c))
    for r in (msg.get_all("Requires-Dist") or []):
        fields.append(("requires_dist", r))
    for u in (msg.get_all("Project-URL") or []):
        fields.append(("project_urls", u))
    for e in (msg.get_all("Provides-Extra") or []):
        fields.append(("provides_extra", e))

    return fields


def create_multipart(fields: list[tuple[str, str]], files: dict[str, tuple[str, bytes]]) -> tuple[bytes, str]:
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = bytearray()

    for key, value in fields:
        if value is None:
            continue
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    for key, (filename, content) in files.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode("utf-8"))
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(content)
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    content_type = f"multipart/form-data; boundary={boundary}"
    return bytes(body), content_type


def upload_file(file_path: Path, token: str, test: bool = False) -> bool:
    target_url = TEST_PYPI_URL if test else PYPI_URL
    filename = file_path.name
    data = file_path.read_bytes()

    is_wheel = filename.endswith(".whl")
    filetype = "bdist_wheel" if is_wheel else "sdist"
    pyversion = "py3" if is_wheel else ""

    fields = extract_metadata(file_path)
    fields.extend([
        ("filetype", filetype),
        ("pyversion", pyversion),
        ("sha256_digest", hashlib.sha256(data).hexdigest()),
        ("md5_digest", hashlib.md5(data).hexdigest()),
        ("blake2_256_digest", hashlib.blake2b(data, digest_size=32).hexdigest()),
    ])

    files = {
        "content": (filename, data)
    }

    body, content_type = create_multipart(fields, files)

    auth_header = "Basic " + base64.b64encode(f"__token__:{token}".encode("utf-8")).decode("ascii")

    req = urllib.request.Request(
        target_url,
        data=body,
        headers={
            "Content-Type": content_type,
            "Authorization": auth_header,
            "User-Agent": "twine/5.1.1 structural-materials-uploader/0.2.0",
        },
    )

    print(f"Uploading {filename} to {target_url}...")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✓ Uploaded {filename} successfully! (Status: {resp.status})")
            return True
    except urllib.error.HTTPError as e:
        error_content = e.read().decode("utf-8", errors="ignore")
        print(f"✗ Failed to upload {filename}: HTTP {e.code} - {e.reason}")
        print(f"Response: {error_content}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    token = os.environ.get("PYPI_TOKEN")
    test_mode = "--test" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--test"]

    if args:
        token = args[0]

    if not token:
        print("Usage: python3 scripts/upload_to_pypi.py <pypi-token> [--test]")
        print("   or: PYPI_TOKEN=<token> python3 scripts/upload_to_pypi.py [--test]")
        sys.exit(1)

    whl = list(DIST.glob("*.whl"))
    sdist = list(DIST.glob("*.tar.gz"))

    if not whl or not sdist:
        print("Building dist archives first...")
        import build_dist
        build_dist.build_wheel()
        build_dist.build_sdist()
        whl = list(DIST.glob("*.whl"))
        sdist = list(DIST.glob("*.tar.gz"))

    all_success = True
    for f in whl + sdist:
        ok = upload_file(f, token, test=test_mode)
        if not ok:
            all_success = False

    if all_success:
        if test_mode:
            print("\n🎉 View package on TestPyPI: https://test.pypi.org/project/structural-materials/")
        else:
            print("\n🎉 View package on PyPI: https://pypi.org/project/structural-materials/")
            print("Install via: pip install structural-materials")


if __name__ == "__main__":
    main()
