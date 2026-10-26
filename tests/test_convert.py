import gzip
import tempfile
import unittest
import zipfile
from pathlib import Path

from bgconvert import bg2mc, convert, nbt, package, region
from bgconvert.cli import _resolve_world, world_spawn


def make_chunk(x: int, z: int) -> bytes:
    blocks = bytearray(4096)
    blocks[0] = 1
    data = bytearray(2048)
    section = b"".join(
        [
            nbt.byte_array_tag("Blocks", blocks),
            nbt.byte_array_tag("Data", data),
            nbt.byte_tag("Y", 0),
            b"\x00",
        ]
    )
    body = b"".join(
        [
            nbt.int_array_tag("HeightMap", [1] * 256),
            nbt.byte_tag("TerrainPopulated", 1),
            nbt.int_tag("xPos", x),
            nbt.int_tag("zPos", z),
            nbt.long_tag("LastUpdate", 0),
            nbt.empty_list_tag("Entities"),
            nbt.empty_list_tag("TileEntities"),
            nbt.byte_array_tag("Biomes", bytes([1] * 256)),
            nbt.compound_list_tag("Sections", [section]),
        ]
    )
    return nbt.root_compound(nbt.compound_tag("Level", body))


class ConvertTests(unittest.TestCase):
    def test_legacy_world_to_bg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            regions = root / "source" / "region"
            regions.mkdir(parents=True)
            region.write_region(regions / "r.0.0.mca", {(0, 0): make_chunk(0, 0)})

            out = root / "out"
            result = convert.convert_world(regions, out, case="legacy")

            self.assertEqual(result.case, "legacy")
            self.assertEqual(result.chunks, 1)
            self.assertEqual(result.empty, 0)
            self.assertTrue((out / "r.0.0.mca").exists())

            found = list(region.iter_chunks(out / "r.0.0.mca"))
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0][0], 0)
            self.assertEqual(found[0][1], 0)
            blocks = found[0][2]["Level"]["Sections"][0]["Blocks"]
            self.assertEqual(blocks[0], 1)

    def test_package_has_matching_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            regions = root / "regions"
            regions.mkdir()
            region.write_region(regions / "r.0.0.mca", {(0, 0): make_chunk(0, 0)})

            out = root / "map"
            zip_path = root / "map.zip"
            package.build_package(regions, out, zip_path)

            files = [p for p in out.rglob("*") if p.is_file()]
            checksum_lines = (out / "checksums.md5").read_text().splitlines()
            self.assertEqual(len(files), len(checksum_lines) + 1)
            self.assertTrue(zip_path.exists())

            with zipfile.ZipFile(zip_path) as archive:
                names = archive.namelist()
            self.assertIn("checksums.md5", names)
            self.assertIn("r.0.0.mca", names)

    def test_finds_the_new_dimension_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            world = Path(tmp)
            regions = world / "dimensions" / "minecraft" / "overworld" / "region"
            regions.mkdir(parents=True)
            found, root = _resolve_world(world)
            self.assertEqual(found, regions)
            self.assertEqual(root, world)

    def test_reads_the_new_spawn_tag(self) -> None:
        self.assertEqual(world_spawn({"spawn": {"pos": [10, 64, 20]}}), (10, 64, 20))
        self.assertEqual(world_spawn({"SpawnX": 1, "SpawnY": 2, "SpawnZ": 3}), (1, 2, 3))


class BgToMcTests(unittest.TestCase):
    def test_bg_zip_becomes_a_world(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            regions = root / "regions"
            regions.mkdir()
            region.write_region(regions / "r.0.0.mca", {(0, 0): make_chunk(0, 0)})
            map_zip = root / "map.zip"
            with zipfile.ZipFile(map_zip, "w") as archive:
                archive.write(regions / "r.0.0.mca", "r.0.0.mca")

            out = root / "world"
            result = bg2mc.main([str(map_zip), "-o", str(out), "--no-empty-chunks", "--force"])
            self.assertEqual(result, 0)
            self.assertTrue((out / "level.dat").exists())
            self.assertTrue((out / "dimensions/minecraft/overworld/region/r.0.0.mca").exists())

            with open(out / "level.dat", "rb") as file:
                world = bg2mc.read_nbt(gzip.decompress(file.read()))[1]
            self.assertEqual(world["Data"]["DataVersion"], 5023)


if __name__ == "__main__":
    unittest.main()
