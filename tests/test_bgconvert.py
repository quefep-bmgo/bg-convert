import tempfile
import unittest
from pathlib import Path

from bgconvert import blocks, decode, nbt, region


class NbtTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        body = b"".join(
            [
                nbt.int_tag("xPos", -12),
                nbt.byte_array_tag("Blocks", bytes([1, 2, 3])),
                nbt.int_array_tag("HeightMap", [0, 1, 255]),
                nbt.compound_list_tag("Sections", [nbt.byte_tag("Y", 3) + b"\x00"]),
                nbt.empty_list_tag("Entities"),
            ]
        )
        raw = nbt.root_compound(nbt.compound_tag("Level", body))
        parsed = nbt.parse(raw)
        level = parsed["Level"]
        self.assertEqual(level["xPos"], -12)
        self.assertEqual(level["Blocks"], bytes([1, 2, 3]))
        self.assertEqual(level["HeightMap"], [0, 1, 255])
        self.assertEqual(level["Sections"], [{"Y": 3}])
        self.assertEqual(level["Entities"], [])


class RegionTests(unittest.TestCase):
    def test_write_then_read(self) -> None:
        raw = nbt.root_compound(nbt.compound_tag("Level", nbt.int_tag("xPos", 7)))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "r.0.0.mca"
            region.write_region(path, {(3, 4): raw})
            found = list(region.iter_chunks(path))
        self.assertEqual(len(found), 1)
        local_x, local_z, chunk = found[0]
        self.assertEqual((local_x, local_z), (3, 4))
        self.assertEqual(chunk["Level"]["xPos"], 7)


class BlockTests(unittest.TestCase):
    def test_known_blocks(self) -> None:
        self.assertEqual(blocks.resolve("minecraft:stone", {}), (1, 0))
        self.assertEqual(blocks.resolve("minecraft:white_wool", {}), (35, 0))
        self.assertEqual(blocks.resolve("minecraft:oak_stairs", {}), (53, 0))
        self.assertEqual(blocks.resolve("minecraft:dark_oak_log", {}), (162, 1))
        self.assertEqual(blocks.resolve("minecraft:sulfur_bricks", {}), (159, 4))
        self.assertEqual(blocks.resolve("minecraft:tuff_bricks", {}), (98, 2))
        self.assertEqual(blocks.resolve("minecraft:cracked_nether_bricks", {}), (112, 0))
        self.assertEqual(blocks.resolve("minecraft:calcite", {}), (155, 0))
        self.assertEqual(blocks.resolve("minecraft:cherry_planks", {}), (159, 0))
        self.assertEqual(blocks.resolve("minecraft:stripped_cherry_wood", {}), (35, 6))
        self.assertEqual(blocks.resolve("minecraft:crimson_planks", {}), (159, 2))
        self.assertEqual(blocks.resolve("minecraft:white_wool_stairs", {}), (156, 0))
        self.assertEqual(blocks.resolve("minecraft:pink_wool_stairs", {}), (203, 0))
        self.assertEqual(blocks.resolve("minecraft:black_wool_stairs", {}), (114, 0))
        self.assertEqual(blocks.resolve("minecraft:pink_wool_slab", {}), (205, 0))
        self.assertEqual(blocks.resolve("minecraft:black_wool_slab", {}), (44, 6))
        self.assertEqual(blocks.resolve("minecraft:light_gray_wool_slab", {}), (44, 0))
        self.assertEqual(blocks.resolve("minecraft:dead_horn_coral_block", {}), (1, 0))
        self.assertIsNone(blocks.resolve("minecraft:does_not_exist", {}))


class PackingTests(unittest.TestCase):
    def test_scheme_detected_by_length(self) -> None:
        self.assertFalse(decode._packed_scheme(5, 342, default_contiguous=True))
        self.assertTrue(decode._packed_scheme(5, 320, default_contiguous=False))
        self.assertTrue(decode._packed_scheme(4, 256, default_contiguous=True))

    def test_readers_agree(self) -> None:
        self.assertEqual(decode._padded_value([0b11111] + [0] * 341, 0, 5, 31), 31)
        self.assertEqual(decode._contiguous_value([0b11111], 0, 5, 31), 31)


if __name__ == "__main__":
    unittest.main()
