"""Generate GLB variants for animation comparison and a final fixed model.

Option A: 3 mesh nodes preserved, each updated to reference a single
          merged skin — minimal structural change.
Option B: 1 new mesh node with all 3 primitives, 1 merged skin — the
          structure Blender produces after Object > Join.
Option C: Same as B but with skeleton=8 (Object_8) set on the merged
          skin so panda3d-gltf computes correct bind poses for all
          joints, fixing feet detachment in non-animating poses.
"""

import struct
from copy import deepcopy
from pathlib import Path
from pygltflib import (
    GLTF2, Mesh, Node, Skin, Accessor, BufferView,
    AnimationChannel, AnimationChannelTarget, AnimationSampler,
)

INPUT = Path("assets/player/calibur_vgdc.glb")
OUTPUT_A = Path("assets/player/calibur_option_a.glb")
OUTPUT_B = Path("assets/player/calibur_option_b.glb")
OUTPUT_C = Path("assets/player/calibur_final.glb")

# Nodes that carry a mesh + skin (found by inspecting the GLB)
MESH_NODES = [(10, 0), (12, 1), (14, 2)]  # (node_idx, skin_idx)


def load() -> tuple[GLTF2, bytearray]:
    gltf = GLTF2().load(str(INPUT))
    return gltf, bytearray(gltf.binary_blob())


def build_merged_skin(
    gltf: GLTF2,
) -> tuple[list[int], list[dict[int, int]]]:
    """Return merged joint list and per-skin remapping dicts."""
    merged: list[int] = []
    for skin in gltf.skins:
        for j in skin.joints:
            if j not in merged:
                merged.append(j)

    remaps = []
    for skin in gltf.skins:
        remaps.append(
            {i: merged.index(j) for i, j in enumerate(skin.joints)}
        )
    return merged, remaps


def remap_joints_blob(
    gltf: GLTF2,
    blob: bytearray,
    node_id: int,
    skin_id: int,
    remap: dict[int, int],
) -> None:
    """Remap JOINTS_0 values in-place for a mesh node."""
    node = gltf.nodes[node_id]
    mesh = gltf.meshes[node.mesh]
    for prim in mesh.primitives:
        if prim.attributes.JOINTS_0 is None:
            continue
        acc = gltf.accessors[prim.attributes.JOINTS_0]
        bv = gltf.bufferViews[acc.bufferView]
        comp_type = acc.componentType
        is_byte = comp_type == 5121  # UNSIGNED_BYTE
        fmt = 'B' if is_byte else 'H'
        comp_size = 1 if is_byte else 2
        stride = bv.byteStride or (4 * comp_size)
        start = (bv.byteOffset or 0) + (acc.byteOffset or 0)
        for i in range(acc.count):
            off = start + i * stride
            vals = list(struct.unpack_from(f'4{fmt}', blob, off))
            struct.pack_into(
                f'4{fmt}', blob, off,
                *[remap.get(v, v) for v in vals]
            )


def build_ibm_accessor(
    gltf: GLTF2,
    blob: bytearray,
    merged_joints: list[int],
) -> tuple[int, bytearray]:
    """Build merged inverse-bind-matrices accessor; return its index."""
    # Collect one IBM per joint node from whichever skin has it first
    ibms: dict[int, tuple[float, ...]] = {}
    for skin in gltf.skins:
        if skin.inverseBindMatrices is None:
            continue
        acc = gltf.accessors[skin.inverseBindMatrices]
        bv = gltf.bufferViews[acc.bufferView]
        start = (bv.byteOffset or 0) + (acc.byteOffset or 0)
        for i, jid in enumerate(skin.joints):
            if jid not in ibms:
                ibms[jid] = struct.unpack_from('16f', blob, start + i * 64)

    identity = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
    ibm_bytes = bytearray()
    for j in merged_joints:
        ibm_bytes.extend(struct.pack('16f', *ibms.get(j, identity)))

    # Align blob to 4 bytes before appending
    while len(blob) % 4:
        blob.append(0)
    offset = len(blob)
    blob.extend(ibm_bytes)

    bv_idx = len(gltf.bufferViews)
    gltf.bufferViews.append(BufferView(
        buffer=0,
        byteOffset=offset,
        byteLength=len(ibm_bytes),
    ))
    acc_idx = len(gltf.accessors)
    gltf.accessors.append(Accessor(
        bufferView=bv_idx,
        byteOffset=0,
        componentType=5126,  # FLOAT
        count=len(merged_joints),
        type="MAT4",
    ))
    return acc_idx, ibm_bytes


def save(gltf: GLTF2, blob: bytearray, path: Path) -> None:
    gltf.buffers[0].byteLength = len(blob)
    gltf.set_binary_blob(bytes(blob))
    gltf.save(str(path))
    print(f"Saved {path}  ({path.stat().st_size // 1024} KB)")


def make_option_a() -> None:
    """3 separate nodes, all sharing 1 merged skin."""
    gltf, blob = load()
    merged_joints, remaps = build_merged_skin(gltf)

    for node_id, skin_id in MESH_NODES:
        if skin_id != 0:
            remap_joints_blob(gltf, blob, node_id, skin_id, remaps[skin_id])

    ibm_acc, _ = build_ibm_accessor(gltf, blob, merged_joints)

    merged_skin_idx = len(gltf.skins)
    gltf.skins.append(Skin(
        joints=merged_joints,
        inverseBindMatrices=ibm_acc,
    ))

    for node_id, _ in MESH_NODES:
        gltf.nodes[node_id].skin = merged_skin_idx

    save(gltf, blob, OUTPUT_A)


def make_option_b() -> None:
    """1 merged node with all 3 primitives + 1 merged skin (Blender join)."""
    gltf, blob = load()
    merged_joints, remaps = build_merged_skin(gltf)

    for node_id, skin_id in MESH_NODES:
        if skin_id != 0:
            remap_joints_blob(gltf, blob, node_id, skin_id, remaps[skin_id])

    ibm_acc, _ = build_ibm_accessor(gltf, blob, merged_joints)

    merged_skin_idx = len(gltf.skins)
    gltf.skins.append(Skin(
        joints=merged_joints,
        inverseBindMatrices=ibm_acc,
    ))

    all_prims = []
    for node_id, _ in MESH_NODES:
        node = gltf.nodes[node_id]
        all_prims.extend(deepcopy(gltf.meshes[node.mesh].primitives))

    merged_mesh_idx = len(gltf.meshes)
    gltf.meshes.append(Mesh(primitives=all_prims))

    merged_node_idx = len(gltf.nodes)
    gltf.nodes.append(Node(
        name="MergedCharacter",
        mesh=merged_mesh_idx,
        skin=merged_skin_idx,
    ))

    # Re-wire: remove old mesh nodes from node-0's children, add merged
    node0 = gltf.nodes[0]
    old_ids = {nid for nid, _ in MESH_NODES}
    node0.children = [
        c for c in (node0.children or []) if c not in old_ids
    ]
    node0.children.append(merged_node_idx)

    save(gltf, blob, OUTPUT_B)


def add_node8_identity_channels(gltf: GLTF2, blob: bytearray) -> None:
    """Add constant identity-TRS animation channels for node 8 to all animations.

    Without this, panda3d-gltf gives Object_8 a CharacterJoint transform of
    csxform (the Y-up→Z-up rotation).  That transform propagates into every
    animated child joint, doubling the coordinate-system conversion and
    displacing the whole body.  Forcing the animation to identity at every
    frame neutralises Object_8 while leaving the bind-pose of non-animated
    joints (feet, lower-legs) intact.
    """
    while len(blob) % 4:
        blob.append(0)

    # Single keyframe at t=0 → panda3d-gltf treats it as constant
    time_off = len(blob)
    blob.extend(struct.pack('f', 0.0))

    trans_off = len(blob)
    blob.extend(struct.pack('3f', 0.0, 0.0, 0.0))   # T = (0,0,0)

    rot_off = len(blob)
    blob.extend(struct.pack('4f', 0.0, 0.0, 0.0, 1.0))  # R = quat identity

    time_bv = len(gltf.bufferViews)
    gltf.bufferViews.append(BufferView(buffer=0, byteOffset=time_off, byteLength=4))
    trans_bv = len(gltf.bufferViews)
    gltf.bufferViews.append(BufferView(buffer=0, byteOffset=trans_off, byteLength=12))
    rot_bv = len(gltf.bufferViews)
    gltf.bufferViews.append(BufferView(buffer=0, byteOffset=rot_off, byteLength=16))

    time_acc = len(gltf.accessors)
    gltf.accessors.append(Accessor(
        bufferView=time_bv, byteOffset=0,
        componentType=5126, count=1, type="SCALAR",
        min=[0.0], max=[0.0],
    ))
    trans_acc = len(gltf.accessors)
    gltf.accessors.append(Accessor(
        bufferView=trans_bv, byteOffset=0,
        componentType=5126, count=1, type="VEC3",
    ))
    rot_acc = len(gltf.accessors)
    gltf.accessors.append(Accessor(
        bufferView=rot_bv, byteOffset=0,
        componentType=5126, count=1, type="VEC4",
    ))

    for anim in gltf.animations:
        si = len(anim.samplers)
        anim.samplers.append(AnimationSampler(input=time_acc, output=trans_acc))
        anim.samplers.append(AnimationSampler(input=time_acc, output=rot_acc))
        anim.channels.append(AnimationChannel(
            sampler=si,
            target=AnimationChannelTarget(node=8, path='translation'),
        ))
        anim.channels.append(AnimationChannel(
            sampler=si + 1,
            target=AnimationChannelTarget(node=8, path='rotation'),
        ))


def make_option_c() -> None:
    """1 merged node + merged skin (skeleton=8) + identity channels for node 8."""
    gltf, blob = load()
    merged_joints, remaps = build_merged_skin(gltf)

    for node_id, skin_id in MESH_NODES:
        if skin_id != 0:
            remap_joints_blob(gltf, blob, node_id, skin_id, remaps[skin_id])

    ibm_acc, _ = build_ibm_accessor(gltf, blob, merged_joints)

    merged_skin_idx = len(gltf.skins)
    gltf.skins.append(Skin(
        joints=merged_joints,
        inverseBindMatrices=ibm_acc,
        skeleton=8,
    ))

    all_prims = []
    for node_id, _ in MESH_NODES:
        node = gltf.nodes[node_id]
        all_prims.extend(deepcopy(gltf.meshes[node.mesh].primitives))

    merged_mesh_idx = len(gltf.meshes)
    gltf.meshes.append(Mesh(primitives=all_prims))

    merged_node_idx = len(gltf.nodes)
    gltf.nodes.append(Node(
        name="MergedCharacter",
        mesh=merged_mesh_idx,
        skin=merged_skin_idx,
    ))

    node0 = gltf.nodes[0]
    old_ids = {nid for nid, _ in MESH_NODES}
    node0.children = [
        c for c in (node0.children or []) if c not in old_ids
    ]
    node0.children.append(merged_node_idx)

    add_node8_identity_channels(gltf, blob)

    save(gltf, blob, OUTPUT_C)


if __name__ == "__main__":
    make_option_a()
    make_option_b()
    make_option_c()
