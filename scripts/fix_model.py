"""
Blender script: inspect, fix and re-export calibur_vgdc.glb.
Run with:  snap run blender --background --python scripts/fix_model.py
"""

import bpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "player" / "calibur_vgdc.glb"
DST = ROOT / "assets" / "player" / "calibur_fixed.glb"

print("\n" + "="*60)
print("STEP 1 — Import")
print("="*60)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.import_scene.gltf(filepath=str(SRC))
print(f"Imported: {SRC}")

# ── STEP 2: inspect ──────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2 — Inspect structure")
print("="*60)

meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
armatures = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']

print(f"Meshes ({len(meshes)}): {[o.name for o in meshes]}")
print(f"Armatures ({len(armatures)}): {[o.name for o in armatures]}")

if not armatures:
    print("ERROR: no armature found — aborting")
    sys.exit(1)

arm = armatures[0]
print(f"Using armature: {arm.name}  ({len(arm.data.bones)} bones)")

# ── STEP 3: filter out meshes with no vertex groups (unweighted) ─
print("\n" + "="*60)
print("STEP 3 — Re-parent & prepare meshes")
print("="*60)

skinned, junk = [], []
for obj in meshes:
    has_vg = len(obj.vertex_groups) > 0
    arm_mods = [m for m in obj.modifiers if m.type == 'ARMATURE']
    mods_str = [m.object.name if m.object else None for m in arm_mods]
    par_str = obj.parent.name if obj.parent else None
    print(f"  {obj.name}: vgroups={len(obj.vertex_groups)}, "
          f"arm_mods={mods_str}, parent={par_str}")

    if not has_vg:
        print("    → NO vertex groups — will delete (unweighted junk mesh)")
        junk.append(obj)
        continue

    skinned.append(obj)

    # Re-point any armature modifier to the main armature
    for m in arm_mods:
        if m.object and m.object != arm:
            print(f"    → re-pointing modifier → {arm.name}")
            m.object = arm
    if not arm_mods:
        print(f"    → adding missing armature modifier")
        mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm

    # Re-parent if needed
    if obj.parent != arm:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.parent_set(type='ARMATURE', keep_transform=True)
        bpy.ops.object.select_all(action='DESELECT')

# Delete junk meshes
for obj in junk:
    bpy.data.objects.remove(obj, do_unlink=True)
print(f"Deleted {len(junk)} unweighted mesh(es)")

# Join all skinned meshes into one
if len(skinned) > 1:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in skinned:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = skinned[0]
    bpy.ops.object.join()
    joined = bpy.context.active_object
    joined.name = "Calibur_Merged"
    print(f"Joined {len(skinned)} meshes → '{joined.name}'")
elif skinned:
    joined = skinned[0]
    print(f"Only 1 mesh, no join needed: '{joined.name}'")
else:
    print("ERROR: no skinned meshes left!")
    sys.exit(1)

# ── STEP 4: vertex groups audit ───────────────────────────────
print("\n" + "="*60)
print("STEP 4 — Vertex groups audit")
print("="*60)

vg_names = {vg.name for vg in joined.vertex_groups}
bone_names = {b.name for b in arm.data.bones}
missing = bone_names - vg_names
extra = vg_names - bone_names

print(f"Vertex groups: {len(vg_names)}")
print(f"Bones: {len(bone_names)}")
print(f"Unweighted bones (no VG): {missing if missing else 'none'}")
print(f"Orphan VGs (no bone): {extra if extra else 'none'}")

# ── STEP 5: weapon attachment audit ───────────────────────────
print("\n" + "="*60)
print("STEP 5 — Weapon bone check")
print("="*60)

keywords = ('weapon', 'sword', 'hand', 'gun', 'item', 'prop')
weapon_bones = [
    b for b in arm.data.bones
    if any(kw in b.name.lower() for kw in keywords)
]
print(f"Candidate attach bones: {[b.name for b in weapon_bones]}")

# Check if the weapon vertices are weighted to Hand.R or similar
for bone in weapon_bones:
    if bone.name in vg_names:
        vg = joined.vertex_groups[bone.name]
        weighted = sum(
            1 for v in joined.data.vertices
            if any(g.group == vg.index for g in v.groups)
        )
        print(f"  {bone.name}: {weighted} weighted vertices")

# ── STEP 6: animation list ────────────────────────────────────
print("\n" + "="*60)
print("STEP 6 — Animations")
print("="*60)

actions = list(bpy.data.actions)
print(f"Actions ({len(actions)}): {[a.name for a in actions]}")

# ── STEP 7: export ────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 7 — Export")
print("="*60)

bpy.ops.export_scene.gltf(
    filepath=str(DST),
    export_format='GLB',
    export_animations=True,
    export_nla_strips=True,
    export_nla_strips_merged_animation_name='',
    export_optimize_animation_size=False,
    export_anim_single_armature=True,
    export_skins=True,
    use_selection=False,
    export_yup=True,
    export_apply=False,
)

size_kb = DST.stat().st_size // 1024
print(f"Exported → {DST}  ({size_kb} KB)")
print("\nAll done.")
