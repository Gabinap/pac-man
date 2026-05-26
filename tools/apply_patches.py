"""Apply patches to third-party packages after uv sync.

Run via `make patch` (called automatically by `make install` and `make build`).
Idempotent: re-running is a no-op if patches are already applied.

Patches the .venv installed packages, which are used by `make run` and by
build_apps to convert GLB→BAM assets during the build step.

Note: ursina's font_setter crash in compiled binaries is fixed via a runtime
monkeypatch in pac-man.py (_patch_ursina_text), not here, because build_apps
re-downloads wheels from PyPI (rejecting local modifications based on hash).
"""

from pathlib import Path
import sys


def _find_site_packages() -> list[Path]:
    roots: list[Path] = []
    for base in (".venv/lib", "venv/lib"):
        root = Path(base)
        if not root.exists():
            continue
        for py in root.iterdir():
            sp = py / "site-packages"
            if sp.exists():
                roots.append(sp)
    return roots


def _find_file(rel: str) -> Path | None:
    for sp in _find_site_packages():
        candidate = sp / rel
        if candidate.exists():
            return candidate
    return None


# ---------------------------------------------------------------------------
# gltf/_converter.py patches
# ---------------------------------------------------------------------------

GLTF_PATCHES: list[tuple[str, str]] = [
    # Bug 1: multiple skins sharing the same skeleton root → previous skinid is
    # overwritten in self.skeletons, losing characters. Fix: store a list.
    # Patches below jump directly from the upstream form to the *final* form
    # (after Bug 5a/5b refinements are factored in), so re-runs against a fully
    # patched file see `new in text` and report cleanly as "already present"
    # instead of false-positive "missing" warnings.
    (
        "        self.skeletons[root_nodeid] = skinid",
        "        self.skeletons.setdefault(root_nodeid, []).append(skinid)",
    ),
    (
        "            if nodeid in self.skeletons:\n"
        "                skinid = self.skeletons[nodeid]\n"
        "                charinfo = CharInfo(node_name)\n"
        "                charinfo.character.set_transform("
        "get_node_transform(gltf_node))\n"
        "                self.build_character("
        "charinfo, nodeid, gltf_data, recurse=True)\n"
        "                self.characters[skinid] = charinfo",
        "            if nodeid in self.skeletons:\n"
        "                for skinid in self.skeletons[nodeid]:\n"
        "                    charinfo = CharInfo(node_name)\n"
        "                    charinfo.character.set_transform("
        "get_node_transform(gltf_node))\n"
        "                    self.build_character("
        "charinfo, nodeid, gltf_data, recurse=True, skinid=skinid)\n"
        "                    self.characters[skinid] = charinfo",
    ),
    (
        "            skinid = self.skeletons.get(nodeid, None)\n"
        "            charinfo = self.characters.get(skinid, None)",
        "            skinids = self.skeletons.get(nodeid, None)\n"
        "            skinid = skinids[0] if skinids is not None else None\n"
        "            charinfo = self.characters.get(skinid, None)\n"
        "            if skinids is not None:\n"
        "                for _sid in skinids[1:]:\n"
        "                    _ci = self.characters.get(_sid)\n"
        "                    if _ci is not None:\n"
        "                        _ci.nodepath.reparent_to(root)",
    ),
    (
        "        if nodeid in self.skeletons:\n"
        "            skinid = self.skeletons[nodeid]\n"
        "            gltf_skin = gltf_data['skins'][skinid]",
        "        if nodeid in self.skeletons:\n"
        "            if skinid is None:\n"
        "                skinid = self.skeletons[nodeid][0]\n"
        "            gltf_skin = gltf_data['skins'][skinid]",
    ),
    # Bug 2: accessors without bufferView crash the sort by KeyError.
    (
        "        accessors = sorted(accessors, key=lambda x: x['bufferView'])",
        "        accessors = [a for a in accessors if 'bufferView' in a]\n"
        "        accessors = sorted(accessors, key=lambda x: x['bufferView'])",
    ),
    # Bug 3: GLBs with multiple disconnected joint roots (no single common
    # joint ancestor) fall into the heuristic branch of build_character that
    # treats each disconnected root as a sibling under <skeleton>. Force the
    # explicit skeleton path using the LCA already computed by load_skin so a
    # single recursive create_joint traversal builds the full tree.
    (
        "        root_nodeid = common_path[-1]\n"
        "\n"
        "        self.skeletons.setdefault(root_nodeid, []).append(skinid)",
        "        root_nodeid = common_path[-1]\n"
        "        gltf_skin['skeleton'] = root_nodeid\n"
        "\n"
        "        self.skeletons.setdefault(root_nodeid, []).append(skinid)",
    ),
    # Bug 4a: original (unpatched) form — pre-mul vertices by inverse(W_mesh).
    (
        "            # Set the transform of the skinned node to the inverse"  # noqa: E501
        " of the parent's\n"
        "            # transform.  This allows skinning to happen in"
        " global space.\n"
        "            net_xform = NodePath(geom_node.get_parent(0))"
        ".get_net_transform()\n"
        "            inverse = net_xform.get_inverse()\n"
        "            gvd.transform_vertices(inverse.get_mat())",
        "            net_xform = NodePath(geom_node.get_parent(0))"
        ".get_net_transform()\n"
        "            _mat = net_xform.get_mat()\n"
        "            _sx = _mat.get_row3(0).length()\n"
        "            _sy = _mat.get_row3(1).length()\n"
        "            _sz = _mat.get_row3(2).length()\n"
        "            if (abs(_sx - 1.0) > 1e-3\n"
        "                    or abs(_sy - 1.0) > 1e-3\n"
        "                    or abs(_sz - 1.0) > 1e-3):\n"
        "                NodePath(geom_node).reparent_to("
        "charinfo.nodepath)\n"
        "            else:\n"
        "                gvd.transform_vertices("
        "net_xform.get_inverse().get_mat())",
    ),
    # Bug 4b: upgrade from the previous unconditional-reparent fix.
    (
        "            # Bypass the mesh node's parent transform chain"
        " (which often\n"
        "            # contains scale=100 on FBX → GLTF armatures); the"
        " GLTF spec\n"
        "            # says the mesh node's world transform must not be"
        " applied to\n"
        "            # skinned vertices.\n"
        "            NodePath(geom_node).reparent_to(charinfo.nodepath)",
        "            net_xform = NodePath(geom_node.get_parent(0))"
        ".get_net_transform()\n"
        "            _mat = net_xform.get_mat()\n"
        "            _sx = _mat.get_row3(0).length()\n"
        "            _sy = _mat.get_row3(1).length()\n"
        "            _sz = _mat.get_row3(2).length()\n"
        "            if (abs(_sx - 1.0) > 1e-3\n"
        "                    or abs(_sy - 1.0) > 1e-3\n"
        "                    or abs(_sz - 1.0) > 1e-3):\n"
        "                NodePath(geom_node).reparent_to("
        "charinfo.nodepath)\n"
        "            else:\n"
        "                gvd.transform_vertices("
        "net_xform.get_inverse().get_mat())",
    ),
    # Bug 5: function signature to thread skinid through the for-loop.
    (
        "    def build_character(self, charinfo: CharInfo, nodeid,"
        " gltf_data, recurse=True):",
        "    def build_character(self, charinfo: CharInfo, nodeid,"
        " gltf_data, recurse=True, skinid=None):",
    ),
    # Fix 5c: attach skinned meshes under their character's nodepath.
    (
        "                else:\n"
        "                    np.attach_new_node(mesh)\n"
        "                    if charinfo:\n"
        "                        self.combine_mesh_skin(mesh, charinfo)\n"
        "                        self.combine_mesh_morphs("
        "mesh, meshid, charinfo)",
        "                else:\n"
        "                    if charinfo:\n"
        "                        charinfo.nodepath.attach_new_node(mesh)\n"
        "                        self.combine_mesh_skin(mesh, charinfo)\n"
        "                        self.combine_mesh_morphs("
        "mesh, meshid, charinfo)\n"
        "                    else:\n"
        "                        np.attach_new_node(mesh)",
    ),
]

# ---------------------------------------------------------------------------
# ursina/text.py patches  (venv only — for `make run` cleanliness)
# ---------------------------------------------------------------------------

URSINA_TEXT_PATCHES: list[tuple[str, str]] = [
    # Bug: font_setter crashes with AttributeError when _search_for_file
    # returns None. The runtime monkeypatch in pac-man.py fixes this in the
    # compiled binary; this venv patch fixes the same issue for `make run`
    # without relying on the try/except wrapper.
    (
        "        if not font_file_path:\n"
        "            print_warning('missing font:', value)\n"
        "\n"
        "        # font = FontPool.load_font(str(font_file_path))\n"
        "        # since FontPool can't import fonts from path on Windows,"
        " add the directory to the \"model path\" and load by name\n"
        "        from panda3d.core import getModelPath\n"
        "        _model_path = getModelPath()\n"
        "        _model_path.append_path("
        "str(font_file_path.parent.resolve()))\n"
        "        font = FontPool.load_font(font_file_path.name)",
        "        if not font_file_path:\n"
        "            font = FontPool.load_font(value)\n"
        "            if not font:\n"
        "                print_warning('missing font:', value)\n"
        "                return\n"
        "        else:\n"
        "            # since FontPool can't import fonts from path on"
        " Windows, add the directory to the \"model path\" and load by"
        " name\n"
        "            from panda3d.core import getModelPath\n"
        "            _model_path = getModelPath()\n"
        "            _model_path.append_path("
        "str(font_file_path.parent.resolve()))\n"
        "            font = FontPool.load_font(font_file_path.name)",
    ),
]


# ---------------------------------------------------------------------------
# Generic patch runner
# ---------------------------------------------------------------------------

def _apply(
    label: str, path: Path, patches: list[tuple[str, str]]
) -> tuple[int, int]:
    """Apply patches to a plain file. Returns (applied, missing) counts."""
    text = path.read_text()
    applied = 0
    missing = 0
    for old, new in patches:
        if new in text:
            pass
        elif old in text:
            text = text.replace(old, new, 1)
            applied += 1
        else:
            hint = old[:60].replace("\n", "\\n")
            print(
                f"WARNING [{label}]: patch not found"
                f" (may need update): {hint!r}"
            )
            missing += 1
    path.write_text(text)
    if applied or missing:
        print(
            f"{label} patches: {applied} applied, "
            f"{len(patches) - applied - missing} already present, "
            f"{missing} missing"
        )
    return applied, missing


def main() -> int:
    """Apply all patches and report results."""
    total_missing = 0

    converter = _find_file("gltf/_converter.py")
    if converter is None:
        print("Skipping gltf patches: gltf/_converter.py not found")
    else:
        _, m = _apply("panda3d-gltf", converter, GLTF_PATCHES)
        total_missing += m

    ursina_text = _find_file("ursina/text.py")
    if ursina_text is None:
        print("Skipping ursina patches: ursina/text.py not found in any venv")
    else:
        _, m = _apply("ursina/text.py", ursina_text, URSINA_TEXT_PATCHES)
        total_missing += m

    return 1 if total_missing else 0


if __name__ == "__main__":
    sys.exit(main())
