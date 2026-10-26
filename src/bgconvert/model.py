from dataclasses import dataclass


@dataclass
class Section:
    y: int
    blocks: bytearray
    data: bytearray


@dataclass
class Chunk:
    x: int
    z: int
    sections: list[Section]
