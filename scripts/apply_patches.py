"""Apply patches to third-party packages after uv sync."""

from pathlib import Path

CONVERTER = Path(".venv/lib/python3.13/site-packages/gltf/_converter.py")

PATCHES: list[tuple[str, str]] = [
    # Bug 1: multiple skins sharing the same skeleton root → KeyError in
    # self.characters[skinid]. Fix: store a list of skinids per root node.
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
    # Bug 2: accessors without bufferView crash the sort.
    (
        "        accessors = sorted(accessors, key=lambda x: x['bufferView'])",
        "        accessors = [a for a in accessors if 'bufferView' in a]\n"
        "        accessors = sorted(accessors, key=lambda x: x['bufferView'])",
    ),
]


def main() -> None:
    if not CONVERTER.exists():
        print(f"Skipping patches: {CONVERTER} not found")
        return

    text = CONVERTER.read_text()
    applied = 0

    for old, new in PATCHES:
        if old in text:
            text = text.replace(old, new, 1)
            applied += 1
        elif new in text:
            pass  # already applied
        else:
            hint = old[:55].replace('\n', '\\n')
            print(f"WARNING: patch not found — may need update: {hint!r}")

    CONVERTER.write_text(text)
    print(
        f"panda3d-gltf patches: {applied} applied, "
        f"{len(PATCHES) - applied} already present"
    )


if __name__ == "__main__":
    main()
