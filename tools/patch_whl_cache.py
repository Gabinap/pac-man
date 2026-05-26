"""Patch panda3d-gltf _converter.py inside __whl_cache__ wheel files.

Run between the two build_apps passes in `make build`.  The first pass
downloads fresh wheels; this script patches gltf/_converter.py inside
each cached panda3d_gltf wheel; the second build_apps pass recompiles
from the patched wheels.

pip skips re-downloading wheels whose filename already exists in the
cache dir, so the patched content is preserved across the second pass.
"""

from __future__ import annotations

import sys
import zipfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.apply_patches import GLTF_PATCHES  # noqa: E402

_TARGET = "gltf/_converter.py"
_CACHE_DIR = Path("build/__whl_cache__")


def _patch_wheel(whl: Path) -> bool:
    with zipfile.ZipFile(whl, "r") as zin:
        if _TARGET not in zin.namelist():
            return False
        text = zin.read(_TARGET).decode("utf-8")

    patched = text
    applied = 0
    for old, new in GLTF_PATCHES:
        if new in patched:
            continue
        if old in patched:
            patched = patched.replace(old, new, 1)
            applied += 1

    if not applied:
        return False

    tmp = whl.with_suffix(".tmp")
    with zipfile.ZipFile(whl, "r") as zin:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                if info.filename == _TARGET:
                    zout.writestr(info, patched.encode("utf-8"))
                elif info.filename.endswith("RECORD"):
                    pass  # skip stale hash manifest
                else:
                    zout.writestr(info, zin.read(info.filename))
    shutil.move(str(tmp), str(whl))
    print(f"  patched {whl.name}: {applied} fix(es)")
    return True


def main() -> int:
    wheels = list(_CACHE_DIR.glob("*/panda3d_gltf-*.whl"))
    if not wheels:
        print(
            "patch-whl-cache: no panda3d_gltf wheel found"
            f" under {_CACHE_DIR} — run `make build` first"
        )
        return 1
    for whl in wheels:
        _patch_wheel(whl)
    return 0


if __name__ == "__main__":
    sys.exit(main())
