"""Convert a legacy Anvil (.mca) map bundle into a Minecraft Java 26.3 world.

Input:
  * a Blockman GO map zip containing r.*.mca + lang/checksums, or
  * a directory containing r.*.mca files.

Output:
  * a Minecraft 26.3 world directory (level.dat + dimensions/...), or
  * a .zip of that world.

The source chunks use the old (<=1.12) numeric Blocks/Data section format.
The target uses the 1.18+ / 26.3 section format:
  sections[] -> Y, block_states { palette, data }, biomes { palette }
  palette entries are {id, properties} compounds when any state has
  properties, otherwise a plain list of block-id strings.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import json
import math
import os
import shutil
import struct
import tempfile
import time
import zipfile
import zlib
from collections import defaultdict

from .legacy_blocks import LEGACY_TABLE

HERE = os.path.dirname(os.path.abspath(__file__))


def _state_key(st):
    if st is None:
        return None
    return (st[0], tuple(sorted(st[1].items())))


LEGACY_KEYS = [_state_key(st) for st in LEGACY_TABLE]

DATA_VERSION = 5023
WORLD_MIN_Y = -64
TARGET_SECTIONS = 24
TARGET_Y_MIN = -4
PLAINS = "minecraft:plains"
AIR_KEY = ("minecraft:air", ())

# ------------------------------------------------------------------ NBT types


class Tag:
    pass


class Byte(int):
    pass


class Short(int):
    pass


class Int(int):
    pass


class Long(int):
    pass


class Float(float):
    pass


class Double(float):
    pass


class ByteArray(bytes):
    pass


class String(str):
    pass


class IntArray(list):
    pass


class LongArray(list):
    pass


class List(list):
    def __init__(self, elem_type=10, items=None):
        super().__init__(items or [])
        self.elem_type = elem_type


class Compound(dict):
    pass


TYPES = {
    Byte: 1, Short: 2, Int: 3, Long: 4, Float: 5, Double: 6,
    ByteArray: 7, String: 8, List: 9, Compound: 10, IntArray: 11,
    LongArray: 12,
}


def tag_type(t):
    for cls, tid in TYPES.items():
        if isinstance(t, cls):
            return tid
    if isinstance(t, bool):
        return 1
    if isinstance(t, int):
        return 3
    if isinstance(t, float):
        return 6
    if isinstance(t, str):
        return 8
    raise TypeError(type(t))


def read_nbt(buf, pos=0):
    def r(fmt):
        nonlocal pos
        v = struct.unpack_from(fmt, buf, pos)[0]
        pos += struct.calcsize(fmt)
        return v

    def name():
        nonlocal pos
        n = struct.unpack_from(">H", buf, pos)[0]
        pos += 2
        s = buf[pos:pos + n].decode("utf-8", "replace")
        pos += n
        return s

    def payload(t):
        nonlocal pos
        if t == 1:
            return Byte(r(">b"))
        if t == 2:
            return Short(r(">h"))
        if t == 3:
            return Int(r(">i"))
        if t == 4:
            return Long(r(">q"))
        if t == 5:
            return Float(r(">f"))
        if t == 6:
            return Double(r(">d"))
        if t == 7:
            n = r(">i")
            v = ByteArray(buf[pos:pos + n])
            pos += n
            return v
        if t == 8:
            n = r(">H")
            v = String(buf[pos:pos + n].decode("utf-8", "replace"))
            pos += n
            return v
        if t == 9:
            et = r(">b")
            n = r(">i")
            return List(et, [payload(et) for _ in range(n)])
        if t == 10:
            o = Compound()
            while True:
                tt = r(">b")
                if tt == 0:
                    return o
                k = name()
                o[k] = payload(tt)
        if t == 11:
            n = r(">i")
            v = IntArray(struct.unpack_from(">" + str(n) + "i", buf, pos))
            pos += 4 * n
            return v
        if t == 12:
            n = r(">i")
            v = LongArray(struct.unpack_from(">" + str(n) + "q", buf, pos))
            pos += 8 * n
            return v
        raise ValueError(f"bad NBT tag {t}")

    t = r(">b")
    return name(), payload(t), pos


def write_nbt(tag, name=""):
    out = bytearray()

    def w(fmt, *v):
        out.extend(struct.pack(fmt, *v))

    def wname(s):
        b = s.encode("utf-8")
        w(">H", len(b))
        out.extend(b)

    def payload(t):
        tid = tag_type(t)
        if tid == 1:
            w(">b", int(t))
        elif tid == 2:
            w(">h", int(t))
        elif tid == 3:
            w(">i", int(t))
        elif tid == 4:
            w(">q", int(t))
        elif tid == 5:
            w(">f", float(t))
        elif tid == 6:
            w(">d", float(t))
        elif tid == 7:
            w(">i", len(t))
            out.extend(bytes(t))
        elif tid == 8:
            wname(str(t))
        elif tid == 9:
            w(">b", t.elem_type)
            w(">i", len(t))
            for x in t:
                payload(x)
        elif tid == 10:
            for k, v in t.items():
                vt = tag_type(v)
                w(">b", vt)
                wname(k)
                payload(v)
            w(">b", 0)
        elif tid == 11:
            w(">i", len(t))
            out.extend(struct.pack(">" + str(len(t)) + "i", *[int(x) for x in t]))
        elif tid == 12:
            w(">i", len(t))
            out.extend(struct.pack(">" + str(len(t)) + "q", *[int(x) for x in t]))
        else:
            raise TypeError(tid)

    tid = tag_type(tag)
    w(">b", tid)
    wname(name)
    payload(tag)
    return bytes(out)


def load_gzip_nbt(path):
    with open(path, "rb") as f:
        data = gzip.decompress(f.read())
    return read_nbt(data)[1]


def save_gzip_nbt(path, tag, name=""):
    with open(path, "wb") as f:
        f.write(gzip.compress(write_nbt(tag, name), compresslevel=6))


# ---------------------------------------------------------------- bit packing


def pack_dense(vals, bits):
    """Dense packing used by 1.16+ block_states (values may straddle longs)."""
    longs = [0] * ((len(vals) * bits + 63) // 64)
    bit = 0
    mask = (1 << bits) - 1
    for v in vals:
        word = bit >> 6
        off = bit & 63
        longs[word] |= (v & mask) << off
        if off + bits > 64:
            longs[word + 1] |= v >> (64 - off)
        longs[word] &= (1 << 64) - 1
        if off + bits > 64:
            longs[word + 1] &= (1 << 64) - 1
        bit += bits
    return [x - (1 << 64) if x >= (1 << 63) else x for x in longs]


def pack_padded(vals, bits):
    """Padded packing used by heightmaps (7 nine-bit entries per long)."""
    per = 64 // bits
    longs = [0] * ((len(vals) + per - 1) // per)
    mask = (1 << bits) - 1
    for i, v in enumerate(vals):
        longs[i // per] |= (v & mask) << ((i % per) * bits)
    return [x - (1 << 64) if x >= (1 << 63) else x for x in longs]


# ---------------------------------------------------------------- region input


def decompress_chunk(raw, comp):
    if raw[:2] == b"\x1f\x8b":
        return gzip.decompress(raw)
    if comp == 2:
        try:
            return zlib.decompress(raw)
        except Exception:
            pass
    if comp == 1:
        try:
            return gzip.decompress(raw)
        except Exception:
            pass
    for fn in (zlib.decompress, gzip.decompress, lambda b: b):
        try:
            return fn(raw)
        except Exception:
            continue
    return None


def iter_region_chunks(data):
    """Yield (xPos, zPos, root) from a region file.

    The sector-count byte in old exports is sometimes wrong, so the span is
    derived from the record's own length field.  Repeated offsets are skipped.
    Bit 0x80 of the first offset byte marks externally stored chunks; those are
    ignored here (the legacy maps in this archive do not use them).
    """
    if len(data) < 8192:
        return
    seen = set()
    for idx in range(1024):
        entry = struct.unpack_from(">I", data, idx * 4)[0]
        if entry == 0 or (entry & 0x80000000):
            continue
        off = (entry >> 8) * 4096
        if off == 0 or off in seen:
            continue
        seen.add(off)
        if off + 5 > len(data):
            continue
        length = struct.unpack_from(">I", data, off)[0]
        if length < 1 or off + 4 + length > len(data):
            continue
        comp = data[off + 4]
        raw = data[off + 5:off + 4 + length]
        dec = decompress_chunk(raw, comp)
        if dec is None:
            continue
        try:
            _, root, _ = read_nbt(dec)
        except Exception:
            continue
        if not isinstance(root, Compound):
            continue
        level = root.get("Level")
        if isinstance(level, Compound):
            x = level.get("xPos")
            z = level.get("zPos")
            if isinstance(x, int) and isinstance(z, int):
                yield int(x), int(z), root
                continue
        # Fallback to the table index only if the chunk has no coordinates.
        yield idx % 32, idx // 32, root


# ---------------------------------------------------------------- target chunk


NON_SOLID_IDS = {
    0, 6, 8, 9, 10, 11, 27, 28, 30, 31, 32, 37, 38, 39, 40, 50, 51, 55, 59,
    63, 65, 66, 68, 69, 70, 72, 75, 76, 77, 78, 83, 90, 92, 93, 94, 96, 101,
    102, 104, 105, 106, 107, 111, 115, 117, 118, 119, 120, 127, 131, 132,
    140, 141, 142, 143, 144, 147, 148, 149, 150, 151, 157, 160, 167, 171,
    175, 176, 177, 178, 198, 199, 200, 207, 209, 217, 255,
}


def build_sections(src_sections, unknown, te_stats):
    """Build 24 26.3 sections from a legacy chunk's Sections list."""
    sections = []
    top_nonair = [0] * 256
    top_motion = [0] * 256

    src_by_y = {}
    for sec in src_sections:
        try:
            y = int(sec.get("Y", 0))
        except Exception:
            continue
        src_by_y[y] = sec

    for ty in range(TARGET_Y_MIN, TARGET_Y_MIN + TARGET_SECTIONS):
        state_keys = [None] * 4096
        sec = src_by_y.get(ty)
        if sec is not None:
            blocks = sec.get("Blocks")
            dat = sec.get("Data")
            add = sec.get("Add")
            if isinstance(blocks, (bytes, bytearray)) and len(blocks) >= 4096:
                if not isinstance(dat, (bytes, bytearray)):
                    dat = b"\0" * 2048
                if not isinstance(add, (bytes, bytearray)) or len(add) < 2048:
                    add = None
                for i in range(4096):
                    b = blocks[i]
                    if not b:
                        continue
                    if add is not None:
                        a = add[i >> 1]
                        b |= (((a >> 4) if (i & 1) else (a & 15)) << 8)
                    d = dat[i >> 1]
                    d = (d >> 4) if (i & 1) else (d & 15)
                    key = LEGACY_KEYS[(b << 4) | d] if b < 256 else LEGACY_KEYS[16]
                    if key is None:
                        continue
                    if key[0] == "minecraft:stone" and b >= 256:
                        unknown.add((b, d))
                    state_keys[i] = key
                    # Heightmap columns use x + z*16; local Y is i >> 8.
                    col = i & 255
                    wy = ty * 16 + (i >> 8) + 1
                    top_nonair[col] = max(top_nonair[col], wy)
                    if b not in NON_SOLID_IDS and wy > top_motion[col]:
                        top_motion[col] = wy

        # Palette.  Air is always index 0 so the layout is deterministic.
        pal = [AIR_KEY]
        index = {AIR_KEY: 0}
        for key in state_keys:
            if key is None:
                continue
            idx = index.get(key)
            if idx is None:
                idx = len(pal)
                index[key] = idx
                pal.append(key)

        bs = Compound()
        if len(pal) == 1:
            bs["palette"] = List(8, [String("minecraft:air")])
        else:
            if any(props for _, props in pal):
                entries = []
                for name, props in pal:
                    c = Compound({"id": String(name)})
                    if props:
                        c["properties"] = Compound({k: String(v) for k, v in props})
                    entries.append(c)
                bs["palette"] = List(10, entries)
            else:
                bs["palette"] = List(8, [String(name) for name, _ in pal])
            bits = max(4, (len(pal) - 1).bit_length())
            vals = [index[key if key is not None else AIR_KEY] for key in state_keys]
            bs["data"] = LongArray(pack_padded(vals, bits))

        section = Compound()
        section["Y"] = Byte(ty)
        section["block_states"] = bs
        section["biomes"] = Compound({"palette": List(8, [String(PLAINS)])})
        sections.append(section)

    height_nonair = [min(511, v + 64) if v else 0 for v in top_nonair]
    height_motion = [min(511, v + 64) if v else 0 for v in top_motion]
    heightmaps = Compound({
        "MOTION_BLOCKING": LongArray(pack_padded(height_motion, 9)),
        "WORLD_SURFACE": LongArray(pack_padded(height_nonair, 9)),
    })
    return sections, heightmaps


def normalize_sign_text(text):
    text = str(text or "")
    if not text:
        return ""
    if text[0] in "{[\"":
        return text
    return json.dumps({"text": text}, ensure_ascii=False)


def build_block_entities(tile_entities, te_stats):
    entities = []
    for te in tile_entities or []:
        if not isinstance(te, Compound):
            continue
        tid = str(te.get("id", ""))
        if tid not in ("Sign", "minecraft:sign"):
            te_stats[tid] = te_stats.get(tid, 0) + 1
            continue
        try:
            x = int(te.get("x", 0))
            y = int(te.get("y", 0))
            z = int(te.get("z", 0))
        except Exception:
            continue
        messages = [String(normalize_sign_text(te.get(f"Text{i}", ""))) for i in range(1, 5)]
        empty = List(8, [String("") for _ in range(4)])
        front = Compound({
            "messages": List(8, messages),
            "color": String("black"),
            "has_glowing_text": Byte(0),
        })
        back = Compound({
            "messages": copy.deepcopy(empty),
            "color": String("black"),
            "has_glowing_text": Byte(0),
        })
        entities.append(Compound({
            "id": String("minecraft:sign"),
            "x": Int(x), "y": Int(y), "z": Int(z),
            "is_waxed": Byte(0),
            "front_text": front,
            "back_text": back,
        }))
    return entities


def build_modern_chunk(gx, gz, root, template_root, unknown, te_stats):
    level = root.get("Level") if isinstance(root, Compound) else None
    if not isinstance(level, Compound):
        level = root
    src_sections = level.get("Sections")
    if not isinstance(src_sections, list):
        src_sections = []
    sections, heightmaps = build_sections(src_sections, unknown, te_stats)
    block_entities = build_block_entities(level.get("TileEntities"), te_stats)

    out = Compound()
    out["Status"] = String("minecraft:full")
    out["zPos"] = Int(gz)
    out["block_entities"] = List(10, block_entities) if block_entities else List(0, [])
    out["yPos"] = Int(TARGET_Y_MIN)
    out["LastUpdate"] = Long(0)
    out["structures"] = Compound({"References": Compound(), "starts": Compound()})
    out["InhabitedTime"] = Long(0)
    out["xPos"] = Int(gx)
    out["Heightmaps"] = heightmaps
    out["sections"] = List(10, sections)
    out["isLightOn"] = Byte(0)
    out["block_ticks"] = List(10, [])
    if "PostProcessing" in template_root:
        out["PostProcessing"] = copy.deepcopy(template_root["PostProcessing"])
    out["DataVersion"] = Int(DATA_VERSION)
    out["fluid_ticks"] = List(0, [])
    return out


def build_empty_chunk(gx, gz, template_root):
    """A full-status all-air chunk, so the game does not generate terrain."""
    sections = []
    for ty in range(TARGET_Y_MIN, TARGET_Y_MIN + TARGET_SECTIONS):
        sections.append(Compound({
            "Y": Byte(ty),
            "block_states": Compound({"palette": List(8, [String("minecraft:air")])}),
            "biomes": Compound({"palette": List(8, [String(PLAINS)])}),
        }))
    zeros = LongArray(pack_padded([0] * 256, 9))
    out = Compound()
    out["Status"] = String("minecraft:full")
    out["zPos"] = Int(gz)
    out["block_entities"] = List(0, [])
    out["yPos"] = Int(TARGET_Y_MIN)
    out["LastUpdate"] = Long(0)
    out["structures"] = Compound({"References": Compound(), "starts": Compound()})
    out["InhabitedTime"] = Long(0)
    out["xPos"] = Int(gx)
    out["Heightmaps"] = Compound({"MOTION_BLOCKING": copy.deepcopy(zeros),
                                  "WORLD_SURFACE": copy.deepcopy(zeros)})
    out["sections"] = List(10, sections)
    out["isLightOn"] = Byte(0)
    out["block_ticks"] = List(10, [])
    if "PostProcessing" in template_root:
        out["PostProcessing"] = copy.deepcopy(template_root["PostProcessing"])
    out["DataVersion"] = Int(DATA_VERSION)
    out["fluid_ticks"] = List(0, [])
    return out


def compress_chunk(root):
    raw = write_nbt(root, "")
    comp = zlib.compress(raw, 6)
    return struct.pack(">IB", len(comp) + 1, 2) + comp


def write_region(path, chunks):
    """chunks: dict local_index -> compressed payload (length+type+data)."""
    header = bytearray(8192)
    body = bytearray()
    sector = 2
    for idx in sorted(chunks):
        payload = chunks[idx]
        padded = (len(payload) + 4095) // 4096 * 4096
        sectors = padded // 4096
        if sector > 0xFFFFFF:
            raise RuntimeError(f"region too large: {path}")
        header[idx * 4:idx * 4 + 3] = struct.pack(">I", sector)[1:]
        header[idx * 4 + 3] = sectors
        body.extend(payload)
        body.extend(b"\0" * (padded - len(payload)))
        sector += sectors
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(header)
        f.write(body)


# ---------------------------------------------------------------- world output


def region_coords(name):
    base = os.path.basename(name)
    if not (base.startswith("r.") and base.endswith(".mca")):
        return None
    parts = base[:-4].split(".")
    if len(parts) != 3:
        return None
    try:
        return int(parts[1]), int(parts[2])
    except ValueError:
        return None


def iter_input_regions(path):
    """Yield (filename, bytes) for every .mca in a directory or zip."""
    if os.path.isdir(path):
        for entry in sorted(os.listdir(path)):
            if entry.lower().endswith(".mca"):
                with open(os.path.join(path, entry), "rb") as f:
                    yield entry, f.read()
        return
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for entry in sorted(z.namelist()):
                if entry.lower().endswith(".mca"):
                    yield os.path.basename(entry), z.read(entry)
        return
    raise SystemExit(f"input is neither a directory nor a zip: {path}")


def choose_spawn(stats, override=None):
    if override:
        return tuple(int(v) for v in override)
    if not stats:
        return 0, 100, 0
    xs = [k[0] for k in stats]
    zs = [k[1] for k in stats]
    cx = (min(xs) + max(xs)) / 2.0
    cz = (min(zs) + max(zs)) / 2.0
    # Prefer the chunk containing the map centre; if it is void, use the
    # nearest non-empty chunk (tie-break on the number of solid blocks).
    centre_gx, centre_gz = round(cx), round(cz)
    centre = stats.get((centre_gx, centre_gz))
    if centre is not None and centre[0] > 0:
        gx, gz, top = centre_gx, centre_gz, centre[1]
    else:
        best = None
        for (gx, gz), (count, top) in stats.items():
            if count <= 0:
                continue
            dist = math.hypot(gx - cx, gz - cz)
            score = (-dist, count)
            if best is None or score > best[0]:
                best = (score, gx, gz, top)
        if best is None:
            return 0, 100, 0
        _, gx, gz, top = best
    y = (top + 2) if top >= 0 else 100
    return gx * 16 + 8, y, gz * 16 + 8


def copy_template(template_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for entry in os.listdir(template_dir):
        src = os.path.join(template_dir, entry)
        dst = os.path.join(out_dir, entry)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    # stale data from the template world
    for stale in (
        os.path.join(out_dir, "level.dat_old"),
        os.path.join(out_dir, "session.lock"),
        os.path.join(out_dir, "dimensions", "minecraft", "overworld",
                     "data", "minecraft", "chunk_tickets.dat"),
    ):
        try:
            os.remove(stale)
        except FileNotFoundError:
            pass
    for dim in ("overworld", "the_nether", "the_end"):
        for sub in ("region", "poi"):
            p = os.path.join(out_dir, "dimensions", "minecraft", dim, sub)
            if os.path.isdir(p):
                shutil.rmtree(p)
    os.makedirs(os.path.join(out_dir, "dimensions", "minecraft", "overworld", "region"),
                exist_ok=True)


def update_level_dat(out_dir, name, spawn, gamemode, difficulty):
    path = os.path.join(out_dir, "level.dat")
    root = load_gzip_nbt(path)
    data = root.get("Data") if isinstance(root, Compound) else None
    if not isinstance(data, Compound):
        data = root
    data["LevelName"] = String(name)
    data["DataVersion"] = Int(DATA_VERSION)
    data["Version"] = Compound({
        "Snapshot": Byte(0),
        "Series": String("main"),
        "Id": Int(DATA_VERSION),
        "Name": String("26.3"),
    })
    data["version_history"] = List(3, [Int(DATA_VERSION)])
    data["initialized"] = Byte(1)
    data["allowCommands"] = Byte(1)
    data["GameType"] = Int({"survival": 0, "creative": 1,
                            "adventure": 2, "spectator": 3}[gamemode])
    data["LastPlayed"] = Long(int(time.time() * 1000))
    ds = data.get("difficulty_settings")
    if not isinstance(ds, Compound):
        ds = Compound()
        data["difficulty_settings"] = ds
    ds["difficulty"] = String(difficulty)
    ds["hardcore"] = Byte(0)
    ds["locked"] = Byte(0)
    data["spawn"] = Compound({
        "pos": List(3, [Int(int(spawn[0])), Int(int(spawn[1])), Int(int(spawn[2]))]),
        "pitch": Float(0.0),
        "yaw": Float(0.0),
        "dimension": String("minecraft:overworld"),
    })
    save_gzip_nbt(path, root, "")


def zip_world(world_dir, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for root, dirs, files in os.walk(world_dir):
            for f in files:
                full = os.path.join(root, f)
                arc = os.path.relpath(full, world_dir).replace(os.sep, "/")
                z.write(full, arc)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Convert a legacy .mca map bundle (Blockman GO) to a Minecraft Java 26.3 world.")
    ap.add_argument("input", help="map zip or directory containing r.*.mca")
    ap.add_argument("-o", "--output", help="output world directory or .zip")
    ap.add_argument("--name", help="Minecraft level name (default: output folder stem)")
    ap.add_argument("--gamemode", choices=["survival", "creative", "adventure", "spectator"],
                    default="creative")
    ap.add_argument("--difficulty", choices=["peaceful", "easy", "normal", "hard"],
                    default="easy")
    ap.add_argument("--spawn", nargs=3, type=int, metavar=("X", "Y", "Z"),
                    help="override the computed spawn")
    ap.add_argument("--offset-x", type=int, default=0, help="shift output chunks on X")
    ap.add_argument("--offset-z", type=int, default=0, help="shift output chunks on Z")
    ap.add_argument("--no-empty-chunks", action="store_true",
                    help="do not write empty chunks inside the source region area")
    ap.add_argument("--force", action="store_true", help="overwrite existing output")
    args = ap.parse_args(argv)

    if not os.path.exists(args.input):
        raise SystemExit(f"input not found: {args.input}")
    if not args.output:
        stem = os.path.splitext(os.path.basename(os.path.abspath(args.input)))[0]
        args.output = os.path.join(os.path.dirname(os.path.abspath(args.input)),
                                   stem + "_26.3")
    if os.path.exists(args.output):
        if not args.force:
            raise SystemExit(f"output exists (use --force): {args.output}")
        if os.path.isdir(args.output):
            shutil.rmtree(args.output)
        else:
            os.remove(args.output)

    zip_out = args.output.lower().endswith(".zip")
    if zip_out:
        workdir = tempfile.mkdtemp(prefix="mapconv_")
        world_dir = os.path.join(workdir, "world")
    else:
        workdir = None
        world_dir = args.output

    template_dir = os.path.join(HERE, "world_template")
    with open(os.path.join(template_dir, "chunk_template.nbt"), "rb") as file:
        template_chunk = read_nbt(file.read())[1]
    copy_template(template_dir, world_dir)
    os.remove(os.path.join(world_dir, "chunk_template.nbt"))

    unknown = set()
    te_stats = {}
    stats = {}
    out_regions = defaultdict(dict)
    source_regions = set()
    chunk_count = 0
    empty_count = 0

    for filename, data in iter_input_regions(args.input):
        rc = region_coords(filename)
        if rc is None:
            continue
        rx, rz = rc
        source_regions.add((rx, rz))
        seen_local = set()
        for gx, gz, root in iter_region_chunks(data):
            ox = gx + args.offset_x
            oz = gz + args.offset_z
            lx, lz = ox & 31, oz & 31
            out_regions[(ox >> 5, oz >> 5)][lz * 32 + lx] = compress_chunk(
                build_modern_chunk(ox, oz, root, template_chunk, unknown, te_stats))
            chunk_count += 1
            seen_local.add((gx - rx * 32, gz - rz * 32))
            # spawn statistics from the source chunk
            level = root.get("Level") if isinstance(root, Compound) else root
            secs = level.get("Sections") if isinstance(level, Compound) else None
            count = 0
            top = -1
            if isinstance(secs, list):
                for sec in secs:
                    if not isinstance(sec, Compound):
                        continue
                    blocks = sec.get("Blocks")
                    if not isinstance(blocks, (bytes, bytearray)):
                        continue
                    try:
                        sy = int(sec.get("Y", 0))
                    except Exception:
                        continue
                    for i, b in enumerate(blocks):
                        if b:
                            count += 1
                            wy = sy * 16 + (i >> 8)
                            if b not in NON_SOLID_IDS and wy > top:
                                top = wy
            stats[(ox, oz)] = (count, top)

        if not args.no_empty_chunks:
            for lx in range(32):
                for lz in range(32):
                    if (lx, lz) in seen_local:
                        continue
                    gx = rx * 32 + lx + args.offset_x
                    gz = rz * 32 + lz + args.offset_z
                    key = (gx >> 5, gz >> 5)
                    idx = (gz & 31) * 32 + (gx & 31)
                    if idx in out_regions[key]:
                        continue
                    out_regions[key][idx] = compress_chunk(
                        build_empty_chunk(gx, gz, template_chunk))
                    empty_count += 1

    if chunk_count == 0:
        raise SystemExit("no chunks found in input")

    spawn = choose_spawn(stats, args.spawn)
    name = args.name or os.path.splitext(os.path.basename(os.path.abspath(args.output)))[0]
    update_level_dat(world_dir, name, spawn, args.gamemode, args.difficulty)

    reg_dir = os.path.join(world_dir, "dimensions", "minecraft", "overworld", "region")
    for (rx, rz), chunks in sorted(out_regions.items()):
        write_region(os.path.join(reg_dir, f"r.{rx}.{rz}.mca"), chunks)

    if zip_out:
        zip_world(world_dir, args.output)
        shutil.rmtree(workdir, ignore_errors=True)

    print(f"source chunks : {chunk_count}")
    print(f"empty chunks  : {empty_count}")
    print(f"regions       : {len(out_regions)}")
    print(f"spawn         : {spawn[0]} {spawn[1]} {spawn[2]}")
    print(f"output        : {args.output}")
    if te_stats:
        print("skipped block entities: " + ", ".join(
            f"{name} x{count}" for name, count in sorted(te_stats.items())))
    if unknown:
        ids = sorted(unknown)
        print("unknown legacy ids: " + ", ".join(f"{bid}:{meta}" for bid, meta in ids[:30]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
