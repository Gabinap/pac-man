"""Convert GLB assets to BAM for use by both make run and the compiled binary.

Run via `make convert-assets` (called automatically by `make install` and
`make build`). Idempotent: skips files whose BAM is already newer than the GLB.

BAM is panda3d's native binary format and is loaded without any plugin.
This eliminates the dependency on panda3d-gltf at game runtime while keeping
the source GLB files for re-conversion when assets change.

Also ensures ursina's default font (OpenSans-Regular.ttf) is present in
assets/fonts/ so that build_apps bundles it and the binary can load it.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

_ASSET_DIRS = [
    Path("assets/models"),
    Path("assets/pacgums"),
]

_URSINA_FONTS = ("OpenSans-Regular.ttf", "VeraMono.ttf")


def _find_gltf2bam() -> Path | None:
    for base in (".venv/bin", "venv/bin"):
        candidate = Path(base) / "gltf2bam"
        if candidate.exists():
            return candidate
    return None


def _find_ursina_fonts_dir() -> Path | None:
    for base in (".venv/lib", "venv/lib"):
        root = Path(base)
        if not root.exists():
            continue
        for match in root.glob("*/site-packages/ursina/fonts"):
            if match.is_dir():
                return match
    return None


def _ensure_fonts() -> None:
    fonts_dir = _find_ursina_fonts_dir()
    if fonts_dir is None:
        print("WARNING: ursina fonts dir not found — skipping font copy")
        return
    dst_dir = Path("assets/fonts")
    dst_dir.mkdir(parents=True, exist_ok=True)
    for name in _URSINA_FONTS:
        src = fonts_dir / name
        dst = dst_dir / name
        if dst.exists():
            continue
        if not src.exists():
            print(f"WARNING: {name} not found in {fonts_dir} — skipping")
            continue
        shutil.copy2(src, dst)
        print(f"  copied {name} -> {dst}")


def main() -> int:
    _ensure_fonts()

    gltf2bam = _find_gltf2bam()
    if gltf2bam is None:
        print("convert-assets: gltf2bam not found — skipping GLB conversion")
        return 0

    converted = 0
    for d in _ASSET_DIRS:
        if not d.exists():
            continue
        for glb in sorted(d.glob("*.glb")):
            bam = glb.with_suffix(".bam")
            if bam.exists() and bam.stat().st_mtime >= glb.stat().st_mtime:
                continue
            result = subprocess.run(
                [str(gltf2bam), str(glb), str(bam)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(
                    f"ERROR: gltf2bam failed for {glb}:\n{result.stderr}"
                )
                return 1
            print(f"  converted {glb} -> {bam.name}")
            converted += 1

    if converted:
        print(f"convert-assets: {converted} file(s) converted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
