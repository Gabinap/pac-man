import importlib.util
import os
import sys
import zipfile
import shutil
from pathlib import Path
from setuptools import setup

sys.path.insert(0, str(Path(__file__).parent))
from tools.apply_patches import GLTF_PATCHES  # noqa: E402

_GLTF_TARGET = "gltf/_converter.py"


def _patch_gltf_wheel(whl_path: str) -> None:
    """Patch gltf/_converter.py inside a downloaded wheel, in-place."""
    p = Path(whl_path)
    with zipfile.ZipFile(p, "r") as zin:
        if _GLTF_TARGET not in zin.namelist():
            return
        text = zin.read(_GLTF_TARGET).decode("utf-8")

    patched, applied = text, 0
    for old, new in GLTF_PATCHES:
        if new not in patched and old in patched:
            patched = patched.replace(old, new, 1)
            applied += 1

    if not applied:
        return

    tmp = p.with_suffix(".tmp")
    with zipfile.ZipFile(p, "r") as zin:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                if info.filename == _GLTF_TARGET:
                    zout.writestr(info, patched.encode("utf-8"))
                elif info.filename.endswith("RECORD"):
                    pass  # drop stale hash manifest
                else:
                    zout.writestr(info, zin.read(info.filename))
    shutil.move(str(tmp), str(p))
    print(f"  patched {p.name} ({applied} fix(es))")


try:
    from direct.dist.commands import build_apps as _BuildAppsCmd

    _URSINA_DATA_SUBDIRS = ("models_compressed", "textures", "fonts")
    _URSINA_STAGE = Path("_ursina_stage")

    class build_apps(_BuildAppsCmd):
        def download_wheels(self, platform: str) -> list[str]:
            paths: list[str] = super().download_wheels(platform)
            for p in paths:
                if "panda3d_gltf" in os.path.basename(p):
                    _patch_gltf_wheel(p)
            return paths

        def run(self) -> None:
            staged = self._stage_ursina_data()
            try:
                super().run()
            finally:
                if staged and _URSINA_STAGE.exists():
                    shutil.rmtree(_URSINA_STAGE)

        def _stage_ursina_data(self) -> bool:
            spec = importlib.util.find_spec("ursina")
            if spec is None or spec.origin is None:
                print("build_apps: ursina not found — skipping data staging")
                return False
            ursina_dir = Path(spec.origin).parent
            if _URSINA_STAGE.exists():
                shutil.rmtree(_URSINA_STAGE)
            for subdir in _URSINA_DATA_SUBDIRS:
                src = ursina_dir / subdir
                if src.exists():
                    shutil.copytree(src, _URSINA_STAGE / subdir)
            patterns: list[str] = list(
                self.include_patterns  # type: ignore[has-type]
            )
            self.include_patterns = patterns + ["_ursina_stage/**"]
            print(f"  staged ursina data from {ursina_dir}")
            return True

    _cmdclass: dict = {"build_apps": build_apps}
except ImportError:
    _cmdclass = {}


setup(
    name="pac-man",
    version="0.1.0",
    cmdclass=_cmdclass,
    options={
        "build_apps": {
            "gui_apps": {
                "pac-man": "pac-man.py",
            },
            "include_patterns": [
                "assets/**",
                "data/config.json",
                "data/highscores.json",
                "shaders/**",
                "mazegenerator-2.0.1-py3-none-any.whl",
            ],
            "exclude_patterns": [
                "**/__pycache__/**",
                "**/*.pyc",
                "pm/**",
                "tools/**",
                ".venv/**",
                "assets/**/*.bam",
            ],
            "platforms": [
                "manylinux2014_x86_64",
                "win_amd64",
            ],
            "plugins": [
                "pandagl",
                "p3openal_audio",
                "p3ffmpeg",
            ],
        },
    },
    install_requires=[
        "panda3d",
        "ursina>=8.3.0",
        "pygltflib>=1.16.5",
    ],
)
