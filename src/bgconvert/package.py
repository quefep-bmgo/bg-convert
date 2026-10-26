import hashlib
import json
import shutil
import zipfile
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "template"
CHECKSUM_FILE = "checksums.md5"


def build_package(
    regions_dir: Path,
    out_dir: Path,
    zip_path: Path,
    icon: Path | None = None,
    init: tuple[int, int, int] = (0, 0, 0),
    birth: tuple[float, float, float] = (0.0, 0.0, 0.0),
    template_dir: Path = TEMPLATE_DIR,
) -> Path:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(template_dir, out_dir)

    for stale in out_dir.glob("r.*.mca"):
        stale.unlink()
    for source in sorted(regions_dir.glob("*.mca")):
        shutil.copy2(source, out_dir / source.name)

    if icon is not None and icon.exists():
        shutil.copy2(icon, out_dir / "icon.png")

    _write_init_pos(out_dir / "config.json", init)
    _write_birth_positions(out_dir / "UGCPVPConfig.json", birth)
    write_checksums(out_dir)
    _write_zip(out_dir, zip_path)
    return out_dir


def write_checksums(package_dir: Path) -> None:
    lines = []
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file() or path.name == CHECKSUM_FILE:
            continue
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        relative = path.relative_to(package_dir).as_posix()
        lines.append(f"{digest} *{relative}")
    (package_dir / CHECKSUM_FILE).write_text("\n".join(lines) + "\n", newline="\n")


def _write_init_pos(path: Path, init: tuple[int, int, int]) -> None:
    x, y, z = init
    path.write_text(json.dumps({"InitPos": {"x": x, "y": y, "z": z}}))


def _write_birth_positions(path: Path, birth: tuple[float, float, float]) -> None:
    x, y, z = birth
    config = json.loads(path.read_text(encoding="utf-8"))
    config["teamSetting"]["birthPositions"] = [
        {"x": x, "y": y, "z": z},
        {"x": x + 4, "y": y, "z": z},
    ]
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def _write_zip(package_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_dir).as_posix())
