"""Apply patches to third-party packages after uv sync.

Run via `make patch` (called automatically by `make install`).
Idempotent: re-running is a no-op if patches are already applied.
"""

from pathlib import Path
import sys


def _find_converter() -> Path | None:
    for base in (".venv/lib", "venv/lib"):
        root = Path(base)
        if not root.exists():
            continue
        for py in root.iterdir():
            candidate = py / "site-packages/gltf/_converter.py"
            if candidate.exists():
                return candidate
    return None


PATCHES: list[tuple[str, str]] = [
    # Bug 1: multiple skins sharing the same skeleton root → previous skinid is
    # overwritten in self.skeletons, losing characters. Fix: store a list.
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
        "charinfo, nodeid, gltf_data, recurse=True)\n"
        "                    self.characters[skinid] = charinfo",
    ),
    (
        "            skinid = self.skeletons.get(nodeid, None)\n"
        "            charinfo = self.characters.get(skinid, None)",
        "            skinids = self.skeletons.get(nodeid, None)\n"
        "            skinid = skinids[0] if skinids is not None else None\n"
        "            charinfo = self.characters.get(skinid, None)",
    ),
    (
        "        if nodeid in self.skeletons:\n"
        "            skinid = self.skeletons[nodeid]\n"
        "            gltf_skin = gltf_data['skins'][skinid]",
        "        if nodeid in self.skeletons:\n"
        "            skinid = self.skeletons[nodeid][0]\n"
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
    # Bug 4: animation deforms the mesh when the skinned mesh node sits under
    # parent transforms with non-unit scale (e.g. FBX → GLTF exports with
    # scale=100 on the armature/mesh node). The original code pre-multiplies
    # vertices by inverse(W_mesh) then relies on the scene graph to reapply
    # W_mesh at render. At bind pose this cancels out, but during animation
    # the skin transform `joint_world_now * inverse(joint_world_bind)` ends
    # up conjugated by W_mesh: `W_mesh * skin * inverse(W_mesh)`. For a pure
    # rotation that's harmless (rotations are preserved by rotation-conjuga-
    # tion), but for non-unit scale the conjugation **multiplies the joint
    # translation components by the scale factor**, amplifying them and
    # blowing the mesh up. Fix: detect a non-unit scale in the chain and, in
    # that case only, reparent the geom directly under the Character so the
    # scale chain never reaches it. Pure-rotation chains keep the original
    # pre-mul behaviour (Grobbo-style models depend on the rotation being
    # cancelled out at render to land in the right orientation).
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
    # Bug 4b: upgrade from the previous unconditional-reparent fix (which
    # broke pure-rotation models like Grobbo) to the conditional version.
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
    # Bug 5: multiple skins sharing the same LCA (Sketchfab/FAB exports with
    # separate meshes for body / eyes / weapon). After Bug 1, build_characters
    # creates one CharInfo per skinid, but build_character internally hardcodes
    # `skinid = self.skeletons[nodeid][0]`, so all CharInfos are clones of
    # skin[0]. Also add_node only reparents skinids[0]'s character to the scene
    # graph and attaches every mesh to that same character — so meshes for the
    # other skins are skinned by joints belonging to orphan characters that
    # never receive animation updates, and they appear static.
    # Fix 5a: thread the loop's skinid through build_character so each CharInfo
    # is built with its own skin's joints/animations.
    (
        "    def build_character(self, charinfo: CharInfo, nodeid,"
        " gltf_data, recurse=True):",
        "    def build_character(self, charinfo: CharInfo, nodeid,"
        " gltf_data, recurse=True, skinid=None):",
    ),
    (
        "        if nodeid in self.skeletons:\n"
        "            skinid = self.skeletons[nodeid][0]\n"
        "            gltf_skin = gltf_data['skins'][skinid]",
        "        if nodeid in self.skeletons:\n"
        "            if skinid is None:\n"
        "                skinid = self.skeletons[nodeid][0]\n"
        "            gltf_skin = gltf_data['skins'][skinid]",
    ),
    (
        "            if nodeid in self.skeletons:\n"
        "                for skinid in self.skeletons[nodeid]:\n"
        "                    charinfo = CharInfo(node_name)\n"
        "                    charinfo.character.set_transform("
        "get_node_transform(gltf_node))\n"
        "                    self.build_character("
        "charinfo, nodeid, gltf_data, recurse=True)\n"
        "                    self.characters[skinid] = charinfo",
        "            if nodeid in self.skeletons:\n"
        "                for skinid in self.skeletons[nodeid]:\n"
        "                    charinfo = CharInfo(node_name)\n"
        "                    charinfo.character.set_transform("
        "get_node_transform(gltf_node))\n"
        "                    self.build_character("
        "charinfo, nodeid, gltf_data, recurse=True, skinid=skinid)\n"
        "                    self.characters[skinid] = charinfo",
    ),
    # Fix 5b: in add_node, reparent ALL characters sharing this LCA to the
    # scene graph (not just skinids[0]), and attach each skinned mesh under
    # its own skin's character so the joints driving its vertices actually
    # belong to a character that's in the scene and receives animation.
    (
        "            skinids = self.skeletons.get(nodeid, None)\n"
        "            skinid = skinids[0] if skinids is not None else None\n"
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


def main() -> int:
    converter = _find_converter()
    if converter is None:
        print("Skipping patches: gltf/_converter.py not found in any venv")
        return 0

    text = converter.read_text()
    applied = 0
    missing = 0

    for old, new in PATCHES:
        if new in text:
            pass
        elif old in text:
            text = text.replace(old, new, 1)
            applied += 1
        else:
            hint = old[:60].replace("\n", "\\n")
            print(f"WARNING: patch not found (may need update): {hint!r}")
            missing += 1

    converter.write_text(text)
    print(
        f"panda3d-gltf patches: {applied} applied, "
        f"{len(PATCHES) - applied - missing} already present, "
        f"{missing} missing"
    )
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
