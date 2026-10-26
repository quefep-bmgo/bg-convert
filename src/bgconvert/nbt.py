import struct
from typing import Any

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12


def parse(data: bytes) -> dict[str, Any]:
    if data[0] != TAG_COMPOUND:
        raise ValueError(f"root tag is {data[0]}, expected a compound")
    name_length = struct.unpack_from(">H", data, 1)[0]
    value, _ = _read_compound(data, 3 + name_length)
    return value


def _read_compound(data: bytes, offset: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while True:
        tag_id = data[offset]
        offset += 1
        if tag_id == TAG_END:
            return result, offset
        name_length = struct.unpack_from(">H", data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8", "replace")
        offset += name_length
        result[name], offset = _read_payload(data, offset, tag_id)


def _read_payload(data: bytes, offset: int, tag_id: int) -> tuple[Any, int]:
    if tag_id == TAG_BYTE:
        return struct.unpack_from(">b", data, offset)[0], offset + 1
    if tag_id == TAG_SHORT:
        return struct.unpack_from(">h", data, offset)[0], offset + 2
    if tag_id == TAG_INT:
        return struct.unpack_from(">i", data, offset)[0], offset + 4
    if tag_id == TAG_LONG:
        return struct.unpack_from(">q", data, offset)[0], offset + 8
    if tag_id == TAG_FLOAT:
        return struct.unpack_from(">f", data, offset)[0], offset + 4
    if tag_id == TAG_DOUBLE:
        return struct.unpack_from(">d", data, offset)[0], offset + 8
    if tag_id == TAG_BYTE_ARRAY:
        length = struct.unpack_from(">i", data, offset)[0]
        offset += 4
        return data[offset:offset + length], offset + length
    if tag_id == TAG_STRING:
        length = struct.unpack_from(">H", data, offset)[0]
        offset += 2
        return data[offset:offset + length].decode("utf-8", "replace"), offset + length
    if tag_id == TAG_LIST:
        element_id = data[offset]
        count = struct.unpack_from(">i", data, offset + 1)[0]
        offset += 5
        items = []
        for _ in range(count):
            item, offset = _read_payload(data, offset, element_id)
            items.append(item)
        return items, offset
    if tag_id == TAG_COMPOUND:
        return _read_compound(data, offset)
    if tag_id == TAG_INT_ARRAY:
        count = struct.unpack_from(">i", data, offset)[0]
        offset += 4
        values = list(struct.unpack_from(f">{count}i", data, offset))
        return values, offset + count * 4
    if tag_id == TAG_LONG_ARRAY:
        count = struct.unpack_from(">i", data, offset)[0]
        offset += 4
        values = list(struct.unpack_from(f">{count}q", data, offset))
        return values, offset + count * 8
    raise ValueError(f"unsupported tag id {tag_id}")


def encode_string(text: str) -> bytes:
    payload = text.encode("utf-8")
    return struct.pack(">H", len(payload)) + payload


def make_tag(name: str, tag_id: int, payload: bytes) -> bytes:
    return struct.pack(">b", tag_id) + encode_string(name) + payload


def byte_tag(name: str, value: int) -> bytes:
    return make_tag(name, TAG_BYTE, struct.pack(">b", value))


def int_tag(name: str, value: int) -> bytes:
    return make_tag(name, TAG_INT, struct.pack(">i", value))


def long_tag(name: str, value: int) -> bytes:
    return make_tag(name, TAG_LONG, struct.pack(">q", value))


def byte_array_tag(name: str, values: bytes | bytearray) -> bytes:
    payload = bytes(values)
    return make_tag(name, TAG_BYTE_ARRAY, struct.pack(">i", len(payload)) + payload)


def int_array_tag(name: str, values: list[int]) -> bytes:
    payload = struct.pack(f">{len(values)}i", *values)
    return make_tag(name, TAG_INT_ARRAY, struct.pack(">i", len(values)) + payload)


def empty_list_tag(name: str) -> bytes:
    return make_tag(name, TAG_LIST, struct.pack(">bi", TAG_COMPOUND, 0))


def compound_tag(name: str, body: bytes) -> bytes:
    return make_tag(name, TAG_COMPOUND, body + b"\x00")


def compound_list_tag(name: str, bodies: list[bytes]) -> bytes:
    payload = struct.pack(">bi", TAG_COMPOUND, len(bodies)) + b"".join(bodies)
    return make_tag(name, TAG_LIST, payload)


def root_compound(body: bytes) -> bytes:
    return struct.pack(">b", TAG_COMPOUND) + encode_string("") + body + b"\x00"
