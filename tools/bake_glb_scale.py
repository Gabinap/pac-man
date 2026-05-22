"""Bake a non-unit uniform scale node out of a GLB.

Some Sketchfab/FAB GLBs (e.g. Crockie) have a node like `Crockie_rig_deform`
with scale=[100, 100, 100] sitting between the scene root and the joints +
mesh. panda3d-gltf renders that incorrectly during animation: even with the
geom reparented under the Character (Bug 4 patch), animated joint translations
remain authored in the local space of a scale=100 parent, and the resulting
world motion is amplified.

This script rewrites the GLB so the same world bind pose / animation is
expressed with the offending node's scale set to [1, 1, 1]. The math:

    Given a node N with uniform scale S, for every descendant D
    (recursively):
      - D.translation       *= S   (or matrix[12..14] *= S if D uses matrix)
      - anim translation outputs targeting D *= S
      - For each mesh used by D: POSITION (and morph POSITION deltas) *= S
      - For each skin used by D: IBM translation column *= S
    Then set N.scale = [1, 1, 1].

World vertex positions, joint world transforms, and animation world motion
are all preserved. Rotations, scales (other than N's), and skin weights are
untouched.

Usage:
    uv run python tools/bake_glb_scale.py \
        assets/models/crockie_vgdc.glb Crockie_rig_deform [--out PATH]

Run again on a baked file: idempotent (no nodes with non-unit scale → no-op).
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any

Gltf = dict[str, Any]

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942

GLTF_FLOAT = 5126


def _read_glb(path: Path) -> tuple[Gltf, bytes]:
    """Read a GLB file and return its JSON and binary chunks."""
    raw = path.read_bytes()
    magic, _version, total = struct.unpack_from("<III", raw, 0)
    if magic != GLB_MAGIC:
        raise ValueError(f"not a GLB: {path}")
    off = 12
    json_bytes: bytes | None = None
    bin_bytes: bytes = b""
    while off < total:
        clen, ctype = struct.unpack_from("<II", raw, off)
        body = raw[off + 8: off + 8 + clen]
        if ctype == CHUNK_JSON:
            json_bytes = body
        elif ctype == CHUNK_BIN:
            bin_bytes = body
        off += 8 + clen
    if json_bytes is None:
        raise ValueError("no JSON chunk")
    return json.loads(json_bytes), bin_bytes


def _write_glb(path: Path, gltf: Gltf, bin_data: bytes) -> None:
    """Write a GLB file from JSON and binary chunks."""
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    json_pad = (-len(json_bytes)) % 4
    json_bytes += b" " * json_pad
    bin_pad = (-len(bin_data)) % 4
    bin_data = bin_data + b"\x00" * bin_pad

    total = 12 + 8 + len(json_bytes) + 8 + len(bin_data)
    out = bytearray()
    out += struct.pack("<III", GLB_MAGIC, 2, total)
    out += struct.pack("<II", len(json_bytes), CHUNK_JSON)
    out += json_bytes
    out += struct.pack("<II", len(bin_data), CHUNK_BIN)
    out += bin_data
    path.write_bytes(bytes(out))


def _accessor_view(
    gltf: Gltf, bin_data: bytearray, acc_idx: int
) -> tuple[int, int, int, int]:
    """Return (offset_in_bin, count, components, elem_stride) for a float
    accessor. Components: VEC2=2, VEC3=3, VEC4=4, MAT4=16, SCALAR=1."""
    acc = gltf["accessors"][acc_idx]
    if acc["componentType"] != GLTF_FLOAT:
        raise ValueError(
            f"accessor {acc_idx} not float ({acc['componentType']})"
        )
    components = {
        "SCALAR": 1,
        "VEC2": 2,
        "VEC3": 3,
        "VEC4": 4,
        "MAT2": 4,
        "MAT3": 9,
        "MAT4": 16,
    }[acc["type"]]
    bv = gltf["bufferViews"][acc["bufferView"]]
    base = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    stride = bv.get("byteStride") or (components * 4)
    return base, count, components, stride


def _read_floats(
    bin_data: bytes | bytearray,
    offset: int,
    count: int,
    components: int,
    stride: int,
) -> list[list[float]]:
    """Read float values from binary data at the given offset."""
    out: list[list[float]] = []
    for i in range(count):
        p = offset + i * stride
        out.append(list(struct.unpack_from(f"<{components}f", bin_data, p)))
    return out


def _write_floats(
    bin_data: bytearray,
    offset: int,
    values: list[list[float]],
    stride: int,
) -> None:
    """Write float values into binary data at the given offset."""
    components = len(values[0])
    for i, v in enumerate(values):
        p = offset + i * stride
        struct.pack_into(f"<{components}f", bin_data, p, *v)


def _find_node_by_name(gltf: Gltf, name: str) -> int:
    """Return index of the node with the given name, or exit."""
    for i, n in enumerate(gltf["nodes"]):
        if n.get("name") == name:
            return i
    raise SystemExit(f"node '{name}' not found")


def _collect_descendants(gltf: Gltf, root_idx: int) -> set[int]:
    """All node indices reachable from root_idx (excluding root_idx itself)."""
    out: set[int] = set()
    stack = list(gltf["nodes"][root_idx].get("children", []))
    while stack:
        nid = stack.pop()
        if nid in out:
            continue
        out.add(nid)
        stack.extend(gltf["nodes"][nid].get("children", []))
    return out


def _scale_node_translation(node: Gltf, s: float) -> None:
    """Scale the translation component of a node by s."""
    if "matrix" in node:
        m = node["matrix"]
        m[12] *= s
        m[13] *= s
        m[14] *= s
    elif "translation" in node:
        t = node["translation"]
        node["translation"] = [t[0] * s, t[1] * s, t[2] * s]


def _scale_position_accessor(
    gltf: Gltf, bin_data: bytearray, acc_idx: int, s: float
) -> None:
    """Scale all positions in a VEC3 float accessor by s."""
    off, n, comp, stride = _accessor_view(gltf, bin_data, acc_idx)
    assert comp == 3, f"POSITION accessor {acc_idx} not VEC3"
    vals = _read_floats(bin_data, off, n, comp, stride)
    vals = [[v[0] * s, v[1] * s, v[2] * s] for v in vals]
    _write_floats(bin_data, off, vals, stride)
    acc = gltf["accessors"][acc_idx]
    if "min" in acc:
        acc["min"] = [v * s for v in acc["min"]]
    if "max" in acc:
        acc["max"] = [v * s for v in acc["max"]]


def bake(input_path: Path, node_name: str, output_path: Path) -> None:
    """Bake the scale of node_name into its descendants and write the GLB."""
    gltf, bin_blob = _read_glb(input_path)
    bin_data = bytearray(bin_blob)

    target_idx = _find_node_by_name(gltf, node_name)
    target = gltf["nodes"][target_idx]
    scale = target.get("scale")
    if scale is None:
        print(
            f"node '{node_name}' has no scale field; nothing to bake",
            file=sys.stderr,
        )
        _write_glb(output_path, gltf, bytes(bin_data))
        return

    sx, sy, sz = scale
    if not (abs(sx - sy) < 1e-4 and abs(sy - sz) < 1e-4):
        raise SystemExit(
            f"non-uniform scale {scale} on '{node_name}' — bake unsupported"
        )
    s = sx
    if abs(s - 1.0) < 1e-4:
        print(
            f"node '{node_name}' already has scale ≈ 1; no-op",
            file=sys.stderr,
        )
        _write_glb(output_path, gltf, bytes(bin_data))
        return

    descendants = _collect_descendants(gltf, target_idx)
    print(f"baking scale={s} from '{node_name}' into {len(descendants)} "
          f"descendant nodes")

    # 1. Scale node translations (and matrix translation column).
    for nid in descendants:
        _scale_node_translation(gltf["nodes"][nid], s)

    # 2. Scale animation translation channels targeting descendants.
    anim_acc_done: set[int] = set()
    for anim in gltf.get("animations", []):
        for ch in anim["channels"]:
            t = ch["target"]
            if t.get("node") not in descendants:
                continue
            if t.get("path") != "translation":
                continue
            sampler = anim["samplers"][ch["sampler"]]
            out_acc = sampler["output"]
            if out_acc in anim_acc_done:
                continue
            anim_acc_done.add(out_acc)
            off, n, comp, stride = _accessor_view(gltf, bin_data, out_acc)
            vals = _read_floats(bin_data, off, n, comp, stride)
            vals = [[c * s for c in v] for v in vals]
            _write_floats(bin_data, off, vals, stride)
    print(f"  scaled {len(anim_acc_done)} animation translation accessors")

    # 3. Scale mesh POSITION (+ morph target POSITION deltas).
    mesh_pos_acc_done: set[int] = set()
    meshes_used: set[int] = set()
    for nid in descendants:
        nd = gltf["nodes"][nid]
        if "mesh" in nd:
            meshes_used.add(nd["mesh"])
    for mesh_idx in meshes_used:
        mesh = gltf["meshes"][mesh_idx]
        for prim in mesh["primitives"]:
            pos_acc = prim["attributes"].get("POSITION")
            if pos_acc is not None and pos_acc not in mesh_pos_acc_done:
                mesh_pos_acc_done.add(pos_acc)
                _scale_position_accessor(gltf, bin_data, pos_acc, s)
            for tgt in prim.get("targets", []):
                tpos = tgt.get("POSITION")
                if tpos is not None and tpos not in mesh_pos_acc_done:
                    mesh_pos_acc_done.add(tpos)
                    _scale_position_accessor(gltf, bin_data, tpos, s)
    print(f"  scaled {len(mesh_pos_acc_done)} mesh position accessors")

    # 4. Scale skin inverseBindMatrices translation column for skins used by
    # descendant nodes.
    skins_used: set[int] = set()
    for nid in descendants:
        nd = gltf["nodes"][nid]
        if "skin" in nd:
            skins_used.add(nd["skin"])
    ibm_acc_done: set[int] = set()
    for skin_idx in skins_used:
        skin = gltf["skins"][skin_idx]
        ibm_acc = skin.get("inverseBindMatrices")
        if ibm_acc is None or ibm_acc in ibm_acc_done:
            continue
        ibm_acc_done.add(ibm_acc)
        off, n, comp, stride = _accessor_view(gltf, bin_data, ibm_acc)
        assert comp == 16, f"IBM accessor {ibm_acc} not MAT4"
        mats = _read_floats(bin_data, off, n, comp, stride)
        # MAT4 column-major: translation is at indices 12, 13, 14.
        for m in mats:
            m[12] *= s
            m[13] *= s
            m[14] *= s
        _write_floats(bin_data, off, mats, stride)
    print(f"  scaled {len(ibm_acc_done)} IBM accessors")

    # 5. Set the node's scale to [1, 1, 1] (drop the field).
    del target["scale"]

    _write_glb(output_path, gltf, bytes(bin_data))
    print(f"wrote {output_path}")


def main() -> int:
    """Parse arguments and run the bake operation."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("node_name")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()
    out = args.out or args.input
    bake(args.input, args.node_name, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
