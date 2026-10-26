import gzip
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from . import decode, nbt, region
from .model import Section

CHUNK_COLUMNS = 256
TARGET_SPAWN_X = 579
TARGET_SPAWN_Z = 466


@dataclass(frozen=True)
class Shift:
    x: int = 0
    z: int = 0
    blocks_y: int = 0


@dataclass
class ConvertResult:
    case: str
    chunks: int = 0
    empty: int = 0
    unknown: Counter = field(default_factory=Counter)


def read_level_data(world_dir: Path) -> dict:
    raw = gzip.decompress((world_dir / "level.dat").read_bytes())
    return nbt.parse(raw)["Data"]


def detect_source_format(region_dir: Path, data_version: int | None = None) -> str:
    for path in region.region_files(region_dir):
        for _, _, chunk in region.iter_chunks(path):
            return decode.detect_case(chunk, data_version)
    if data_version is None:
        raise ValueError(f"no readable chunks in {region_dir}")
    return decode.detect_case({}, data_version)


def spawn_shift(spawn_x: int, spawn_z: int, target_x: int, target_z: int) -> Shift:
    return Shift(x=(target_x >> 4) - (spawn_x >> 4), z=(target_z >> 4) - (spawn_z >> 4))


def convert_world(
    region_dir: Path,
    out_dir: Path,
    shift: Shift | None = None,
    case: str = "auto",
    data_version: int | None = None,
) -> ConvertResult:
    if shift is None:
        shift = Shift()
    if case == "auto":
        case = detect_source_format(region_dir, data_version)
    decoder = decode.DECODERS.get(case)
    if decoder is None:
        raise ValueError(f"unknown case {case!r}")

    result = ConvertResult(case=case)
    regions: dict[tuple[int, int], dict[tuple[int, int], bytes]] = {}
    for path in region.region_files(region_dir):
        for _, _, chunk in region.iter_chunks(path):
            converted, unknown = decoder(chunk, shift.blocks_y)
            result.unknown.update(unknown)
            if not converted.sections:
                result.empty += 1
                continue
            gx = converted.x + shift.x
            gz = converted.z + shift.z
            raw = build_chunk(gx, gz, converted.sections)
            regions.setdefault((gx >> 5, gz >> 5), {})[(gx & 31, gz & 31)] = raw
            result.chunks += 1

    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("*.mca"):
        stale.unlink()
    for (rx, rz), chunks in sorted(regions.items()):
        region.write_region(out_dir / f"r.{rx}.{rz}.mca", chunks)
    return result


def build_chunk(gx: int, gz: int, sections: list[Section]) -> bytes:
    body = b"".join(
        [
            nbt.int_array_tag("HeightMap", _heightmap(sections)),
            nbt.byte_tag("TerrainPopulated", 1),
            nbt.int_tag("xPos", gx),
            nbt.int_tag("zPos", gz),
            nbt.long_tag("LastUpdate", 0),
            nbt.empty_list_tag("Entities"),
            nbt.empty_list_tag("TileEntities"),
            nbt.byte_array_tag("Biomes", bytes([1]) * CHUNK_COLUMNS),
            nbt.compound_list_tag("Sections", [_section_body(s) for s in sections]),
        ]
    )
    return nbt.root_compound(nbt.compound_tag("Level", body))


def _section_body(section: Section) -> bytes:
    return b"".join(
        [
            nbt.byte_array_tag("Blocks", section.blocks),
            nbt.byte_array_tag("Data", section.data),
            nbt.byte_array_tag("BlockLight", bytes(2048)),
            nbt.byte_array_tag("SkyLight", bytes([0xFF]) * 2048),
            nbt.byte_tag("Y", section.y),
            b"\x00",
        ]
    )


def _heightmap(sections: list[Section]) -> list[int]:
    heights = [0] * CHUNK_COLUMNS
    for section in sections:
        for z in range(16):
            for x in range(16):
                column = z * 16 + x
                for y in range(15, -1, -1):
                    if section.blocks[y * 256 + column]:
                        heights[column] = section.y * 16 + y + 1
                        break
    return heights
