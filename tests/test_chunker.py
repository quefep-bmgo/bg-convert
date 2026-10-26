import tempfile
import unittest
from pathlib import Path

from bgconvert import chunker, cli


class ChunkerTests(unittest.TestCase):
    def test_version_formats(self) -> None:
        self.assertEqual(chunker.format_name("1.12.2"), "JAVA_1_12_2")
        self.assertEqual(chunker.format_name("1.20.1"), "JAVA_1_20_1")
        self.assertEqual(chunker.format_name("26.3"), "JAVA_26_3")

    def test_unknown_version_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            chunker.format_name("1.7.10")

    def test_explicit_jar_must_exist(self) -> None:
        with self.assertRaises(chunker.ChunkerError):
            chunker.resolve_jar(Path("missing-chunker.jar"))

    def test_explicit_jar_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chunker.jar"
            path.write_bytes(b"test")
            self.assertEqual(chunker.resolve_jar(path), path)

    def test_checksum_reader(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "file"
            path.write_bytes(b"abc")
            self.assertEqual(
                chunker.sha256(path),
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            )

    def test_cli_rejects_a_target_below_the_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "map.zip"
            source.write_bytes(b"not a real map")
            result = cli.main(["to-mc", str(source), "--mc-version", "1.7.10"])
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
