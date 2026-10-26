import gzip
import struct
import zlib
from collections.abc import Iterator
from pathlib import Path

from . import nbt

SECTOR_BYTES = 4096
HEADER_BYTES = SECTOR_BYTES * 2
CHUNKS_PER_REGION = 1024
REGION_WIDTH = 32

COMPRESSION_GZIP = 1
COMPRESSION_ZLIB = 2
COMPRESSION_NONE = 3


def region_files(directory: Path) -> list[Path]:
    files = list(directory.glob("*.mca"))
    files += [path for path in directory.glob("*.mcr") if path not in files]
    return sorted(files)


def _decompress(payload: bytes, compression: int) -> bytes:
    # Old worlds gzip their chunks even while the type byte claims zlib, so trust the magic.
    if payload[:2] == b"\x1f\x8b":
        return gzip.decompress(payload)
    if compression == COMPRESSION_NONE:
        return payload
    return zlib.decompress(payload)


def iter_chunks(path: Path) -> Iterator[tuple[int, int, dict]]:
    data = path.read_bytes()
    if len(data) < HEADER_BYTES:
        return
    for slot in range(CHUNKS_PER_REGION):
        offset = struct.unpack_from(">I", b"\x00" + data[slot * 4:slot * 4 + 3])[0]
        if offset == 0:
            continue
        base = offset * SECTOR_BYTES
        length = struct.unpack_from(">I", data, base)[0]
        if length <= 0:
            continue
        payload = data[base + 5:base + 5 + length - 1]
        try:
            chunk = nbt.parse(_decompress(payload, data[base + 4]))
        except Exception:  # noqa: BLE001, S112 - skip a damaged chunk
            continue
        yield slot % REGION_WIDTH, slot // REGION_WIDTH, chunk


def write_region(path: Path, chunks: dict[tuple[int, int], bytes]) -> None:
    """Each offset entry holds the sector number flat in its low three bytes. Shift it left by
    eight and the game reads zero chunks — this one bites everyone once."""
    offsets = bytearray(SECTOR_BYTES)
    timestamps = bytearray(SECTOR_BYTES)
    body = bytearray()
    sector = 2
    for (local_x, local_z), raw in chunks.items():
        compressed = zlib.compress(raw, 6)
        length = len(compressed) + 1
        sectors = (length + 4 + SECTOR_BYTES - 1) // SECTOR_BYTES
        entry = struct.pack(">I", sector)[1:] + struct.pack(">B", sectors)
        index = (local_x % REGION_WIDTH) + (local_z % REGION_WIDTH) * REGION_WIDTH
        offsets[index * 4:index * 4 + 4] = entry
        body += struct.pack(">I", length)
        body += bytes([COMPRESSION_ZLIB])
        body += compressed
        body += b"\x00" * (sectors * SECTOR_BYTES - length - 4)
        sector += sectors
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(offsets) + bytes(timestamps) + bytes(body))
