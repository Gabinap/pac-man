"""Downscale all game assets in-place.

Textures (JPG/PNG): resized to MAX_SIZE×MAX_SIZE max.
GLB models/pacgums: embedded textures extracted, resized, re-packed.

Run from the project root:
    uv run python3 tools/compress_assets.py
"""

import io
import json
import struct
from pathlib import Path

from PIL import Image

MAX_SIZE = 512
ASSETS = Path("assets")


# ── GLB helpers ──────────────────────────────────────────────────────────────

def _compress_glb(path: Path) -> tuple[int, int]:
    """Resize embedded textures in a GLB. Returns (old_bytes, new_bytes)."""
    raw = path.read_bytes()
    old_size = len(raw)

    magic, _version, _total = struct.unpack_from("<III", raw, 0)
    if magic != 0x46546C67:
        return old_size, old_size  # not a GLB

    # JSON chunk
    json_len, json_type = struct.unpack_from("<II", raw, 12)
    if json_type != 0x4E4F534A:
        return old_size, old_size
    gltf = json.loads(raw[20:20 + json_len])

    # BIN chunk (optional)
    bin_start = 12 + 8 + json_len
    if bin_start >= len(raw):
        return old_size, old_size
    bin_len, bin_type = struct.unpack_from("<II", raw, bin_start)
    if bin_type != 0x004E4942:
        return old_size, old_size
    bin_data = bytearray(raw[bin_start + 8:bin_start + 8 + bin_len])

    images = gltf.get("images", [])
    buffer_views = gltf.get("bufferViews", [])
    if not images or not buffer_views:
        return old_size, old_size

    img_bv: dict[int, str] = {}  # bufferView index → mimeType
    for img in images:
        if img.get("bufferView") is not None:
            img_bv[img["bufferView"]] = img.get("mimeType", "image/jpeg")

    # Rebuild BIN by iterating bufferViews sorted by offset
    sorted_bv = sorted(range(len(buffer_views)),
                       key=lambda i: buffer_views[i].get("byteOffset", 0))
    new_bin = bytearray()
    changed = False

    for bv_idx in sorted_bv:
        bv = buffer_views[bv_idx]
        offset = bv.get("byteOffset", 0)
        length = bv["byteLength"]
        chunk = bytes(bin_data[offset:offset + length])

        # 4-byte alignment padding
        while len(new_bin) % 4:
            new_bin.append(0)

        if bv_idx in img_bv:
            mime = img_bv[bv_idx]
            try:
                pil: Image.Image = Image.open(io.BytesIO(chunk))
                if pil.width > MAX_SIZE or pil.height > MAX_SIZE:
                    mode = "RGBA" if mime == "image/png" else "RGB"
                    pil = pil.convert(mode)
                    pil.thumbnail(
                        (MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS
                    )
                    out = io.BytesIO()
                    if mime == "image/png":
                        pil.save(out, format="PNG", optimize=True)
                    else:
                        pil.save(out, format="JPEG", quality=85, optimize=True)
                    chunk = out.getvalue()
                    changed = True
            except Exception:
                pass  # leave chunk unchanged on error

        bv["byteOffset"] = len(new_bin)
        bv["byteLength"] = len(chunk)
        new_bin.extend(chunk)

    if not changed:
        return old_size, old_size

    for buf in gltf.get("buffers", []):
        buf["byteLength"] = len(new_bin)

    # Rebuild JSON chunk (space-padded to 4-byte boundary)
    json_bytes = bytearray(json.dumps(gltf, separators=(",", ":")).encode())
    while len(json_bytes) % 4:
        json_bytes.append(ord(" "))

    # Rebuild BIN chunk (zero-padded to 4-byte boundary)
    while len(new_bin) % 4:
        new_bin.append(0)

    total = 12 + 8 + len(json_bytes) + 8 + len(new_bin)
    out_buf = bytearray()
    out_buf += struct.pack("<III", 0x46546C67, 2, total)
    out_buf += struct.pack("<II", len(json_bytes), 0x4E4F534A)
    out_buf += json_bytes
    out_buf += struct.pack("<II", len(new_bin), 0x004E4942)
    out_buf += new_bin

    path.write_bytes(out_buf)
    return old_size, len(out_buf)


# ── Texture helpers ──────────────────────────────────────────────────────────

def _compress_texture(path: Path) -> tuple[int, int]:
    """Resize a JPG/PNG texture file. Returns (old_bytes, new_bytes)."""
    old_size = path.stat().st_size
    try:
        img = Image.open(path)
        if img.width <= MAX_SIZE and img.height <= MAX_SIZE:
            return old_size, old_size
        img.thumbnail((MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS)
        ext = path.suffix.lower()
        if ext == ".png":
            img.save(path, format="PNG", optimize=True)
        else:
            img.save(path, format="JPEG", quality=85, optimize=True)
    except Exception as e:
        print(f"  ERROR {path.name}: {e}")
        return old_size, old_size
    return old_size, path.stat().st_size


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    total_saved = 0

    glb_files = sorted(
        list((ASSETS / "models").glob("*.glb"))
        + list((ASSETS / "pacgums").glob("*.glb"))
    )
    tex_files = sorted(
        list((ASSETS / "textures").glob("*.jpg"))
        + list((ASSETS / "textures").glob("*.jpeg"))
        + list((ASSETS / "textures").glob("*.png"))
    )

    print(f"Processing {len(glb_files)} GLB files…")
    for p in glb_files:
        if p.name.endswith(".bak"):
            continue
        old, new = _compress_glb(p)
        saved = old - new
        total_saved += saved
        status = f"-{saved // 1024:>6} KB" if saved > 0 else "  unchanged"
        print(
            f"  {p.name:<40} {old // 1024:>6} KB"
            f" → {new // 1024:>6} KB  {status}"
        )

    print(f"\nProcessing {len(tex_files)} texture files…")
    for p in tex_files:
        old, new = _compress_texture(p)
        saved = old - new
        total_saved += saved
        status = f"-{saved // 1024:>6} KB" if saved > 0 else "  unchanged"
        print(
            f"  {p.name:<40} {old // 1024:>6} KB"
            f" → {new // 1024:>6} KB  {status}"
        )

    print(
        f"\nTotal saved: {total_saved // 1024 // 1024} MB"
        f"  ({total_saved // 1024} KB)"
    )


if __name__ == "__main__":
    main()
