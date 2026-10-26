from collections import Counter
from collections.abc import Mapping
from typing import Any

from . import blocks
from .model import Chunk, Section

U64 = 0xFFFFFFFFFFFFFFFF
SECTIONS_PER_CHUNK = 16
BLOCKS_PER_SECTION = 4096
DATA_BYTES_PER_SECTION = 2048
MIN_BITS = 4

MODERN = "modern"
PALETTED = "paletted"
LEGACY = "legacy"
BETA = "beta"


class Canvas:
    def __init__(self) -> None:
        self.blocks = [bytearray(BLOCKS_PER_SECTION) for _ in range(SECTIONS_PER_CHUNK)]
        self.data = [bytearray(DATA_BYTES_PER_SECTION) for _ in range(SECTIONS_PER_CHUNK)]

    def put(self, world_y: int, local_x: int, local_z: int, block: int, meta: int) -> None:
        if world_y < 0 or world_y > 255:
            return
        section = world_y // 16
        index = (world_y % 16) * 256 + local_z * 16 + local_x
        self.blocks[section][index] = block
        if meta:
            nibble = index >> 1
            if index & 1:
                self.data[section][nibble] = (self.data[section][nibble] & 0x0F) | (meta << 4)
            else:
                self.data[section][nibble] = (self.data[section][nibble] & 0xF0) | meta

    def put_section(self, section_y: int, block_data: bytes, meta_data: bytes) -> None:
        if not 0 <= section_y < SECTIONS_PER_CHUNK:
            return
        self.blocks[section_y][:] = block_data[:BLOCKS_PER_SECTION].ljust(BLOCKS_PER_SECTION, b"\x00")
        self.data[section_y][:] = meta_data[:DATA_BYTES_PER_SECTION].ljust(DATA_BYTES_PER_SECTION, b"\x00")

    def sections(self) -> list[Section]:
        return [
            Section(y, self.blocks[y], self.data[y])
            for y in range(SECTIONS_PER_CHUNK)
            if any(self.blocks[y])
        ]


def detect_case(chunk: dict[str, Any], data_version: int | None = None) -> str:
    if "sections" in chunk:
        return MODERN
    level = chunk.get("Level")
    if level is not None:
        sections = level.get("Sections")
        if sections:
            keys = sections[0].keys()
            if "Palette" in keys:
                return PALETTED
            if "Blocks" in keys:
                return LEGACY
        if "Blocks" in level:
            return BETA
    if data_version is None:
        raise ValueError("cannot detect the chunk format")
    if data_version >= 2825:
        return MODERN
    if data_version >= 1451:
        return PALETTED
    return LEGACY


def decode_modern(chunk: dict[str, Any], shift_y: int) -> tuple[Chunk, Counter]:
    canvas = Canvas()
    unknown: Counter = Counter()
    for section in chunk.get("sections", []):
        states = section.get("block_states")
        if states is None:
            continue
        palette = [_map_entry(entry, unknown) for entry in states["palette"]]
        data = states.get("data")
        section_y = section["Y"]
        if data is None or len(palette) == 1:
            _fill_layer(canvas, section_y, shift_y, palette[0])
            continue
        bits = max(MIN_BITS, (len(palette) - 1).bit_length())
        mask = (1 << bits) - 1
        contiguous = _packed_scheme(bits, len(data), default_contiguous=False)
        for y in range(16):
            world_y = section_y * 16 + y + shift_y
            for z in range(16):
                for x in range(16):
                    index = y * 256 + z * 16 + x
                    if contiguous:
                        palette_index = _contiguous_value(data, index, bits, mask)
                    else:
                        palette_index = _padded_value(data, index, bits, mask)
                    block, meta = palette[palette_index]
                    if block:
                        canvas.put(world_y, x, z, block, meta)
    return _make_chunk(chunk["xPos"], chunk["zPos"], canvas), unknown


def decode_paletted(chunk: dict[str, Any], shift_y: int) -> tuple[Chunk, Counter]:
    canvas = Canvas()
    unknown: Counter = Counter()
    level = chunk["Level"]
    for section in level.get("Sections", []):
        palette = section.get("Palette")
        if palette is None:
            continue
        mapped = [_map_entry(entry, unknown) for entry in palette]
        states = section.get("BlockStates")
        section_y = section["Y"]
        if states is None or len(mapped) == 1:
            _fill_layer(canvas, section_y, shift_y, mapped[0])
            continue
        bits = max(MIN_BITS, (len(mapped) - 1).bit_length())
        mask = (1 << bits) - 1
        contiguous = _packed_scheme(bits, len(states), default_contiguous=True)
        for y in range(16):
            world_y = section_y * 16 + y + shift_y
            for z in range(16):
                for x in range(16):
                    index = y * 256 + z * 16 + x
                    if contiguous:
                        palette_index = _contiguous_value(states, index, bits, mask)
                    else:
                        palette_index = _padded_value(states, index, bits, mask)
                    block, meta = mapped[palette_index]
                    if block:
                        canvas.put(world_y, x, z, block, meta)
    return _make_chunk(level["xPos"], level["zPos"], canvas), unknown


def decode_legacy(chunk: dict[str, Any], shift_y: int) -> tuple[Chunk, Counter]:
    canvas = Canvas()
    level = chunk["Level"]
    for section in level.get("Sections", []):
        block_data = section.get("Blocks")
        if not block_data or len(block_data) != BLOCKS_PER_SECTION:
            continue
        meta_data = section.get("Data") or bytes(DATA_BYTES_PER_SECTION)
        canvas.put_section(section["Y"] + shift_y, block_data, meta_data)
    return _make_chunk(level["xPos"], level["zPos"], canvas), Counter()


def decode_beta(chunk: dict[str, Any], shift_y: int) -> tuple[Chunk, Counter]:
    canvas = Canvas()
    level = chunk["Level"]
    block_data = level.get("Blocks", bytes(32768))
    if len(block_data) < 32768:
        return _make_chunk(level["xPos"], level["zPos"], canvas), Counter()
    meta_data = level.get("Data", bytes(16384))
    for section_y in range(8):
        slice_blocks = block_data[section_y * 4096:(section_y + 1) * 4096]
        if not any(slice_blocks):
            continue
        slice_meta = meta_data[section_y * 2048:(section_y + 1) * 2048]
        canvas.put_section(section_y + shift_y, slice_blocks, slice_meta)
    return _make_chunk(level["xPos"], level["zPos"], canvas), Counter()


DECODERS = {
    MODERN: decode_modern,
    PALETTED: decode_paletted,
    LEGACY: decode_legacy,
    BETA: decode_beta,
}


def _make_chunk(x: int, z: int, canvas: Canvas) -> Chunk:
    return Chunk(x, z, canvas.sections())


def _map_entry(entry: Any, unknown: Counter) -> tuple[int, int]:
    name, properties = _entry_name(entry)
    result = blocks.resolve(name, properties)
    if result is None:
        unknown[name.split(":")[-1]] += 1
        return blocks.FALLBACK_BLOCK
    return result


def _entry_name(entry: Any) -> tuple[str, Mapping[str, Any]]:
    """Palette entries moved around between releases: 1.13-1.17 use Name/Properties, some
    later chunks store a bare name string, and the newest ones use id/properties for stateful
    blocks but an empty-name key for plain ones. Take whichever shape shows up."""
    if isinstance(entry, str):
        return entry, {}
    if isinstance(entry, Mapping):
        if "Name" in entry:
            return entry["Name"], entry.get("Properties") or {}
        if "id" in entry:
            return entry["id"], entry.get("properties") or {}
        if "" in entry:
            return entry[""], {}
        for value in entry.values():
            if isinstance(value, str):
                return value, {}
    return "minecraft:air", {}


def _fill_layer(canvas: Canvas, section_y: int, shift_y: int, block_meta: tuple[int, int]) -> None:
    block, meta = block_meta
    if not block:
        return
    for y in range(16):
        world_y = section_y * 16 + y + shift_y
        for z in range(16):
            for x in range(16):
                canvas.put(world_y, x, z, block, meta)


def _packed_scheme(bits: int, length: int, default_contiguous: bool) -> bool:
    """Which packing is this? The array length gives it away: padded wastes the tail of every
    long, contiguous spills over into the next one. Above four bits the two lengths never match,
    so there's no guessing — and at four bits they're the same anyway."""
    values_per_word = 64 // bits
    padded_length = (BLOCKS_PER_SECTION + values_per_word - 1) // values_per_word
    contiguous_length = (BLOCKS_PER_SECTION * bits + 63) // 64
    if length == padded_length and length != contiguous_length:
        return False
    if length == contiguous_length and length != padded_length:
        return True
    return default_contiguous


def _padded_value(data: list[int], index: int, bits: int, mask: int) -> int:
    # The NBT reader hands back signed words, so mask first or Python sign-extends the shift.
    values_per_word = 64 // bits
    word = index // values_per_word
    if word >= len(data):
        return 0
    offset = (index % values_per_word) * bits
    return ((data[word] & U64) >> offset) & mask


def _contiguous_value(data: list[int], index: int, bits: int, mask: int) -> int:
    bit_position = index * bits
    word = bit_position >> 6
    if word >= len(data):
        return 0
    offset = bit_position & 63
    low = data[word] & U64
    if offset + bits <= 64:
        return (low >> offset) & mask
    high = (data[word + 1] & U64) if word + 1 < len(data) else 0
    return ((low >> offset) | (high << (64 - offset))) & mask
