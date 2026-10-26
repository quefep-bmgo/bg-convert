"""Command line tools for moving worlds between Minecraft and Blockman GO."""

import argparse
import sys
from pathlib import Path

from . import __version__, bg2mc, convert, decode, install, package, region

DEFAULT_TARGET = (convert.TARGET_SPAWN_X, convert.TARGET_SPAWN_Z)


def _level_root(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        if (candidate / "level.dat").is_file():
            return candidate
    return None


def _resolve_world(path: Path) -> tuple[Path, Path | None]:
    world = _level_root(path)
    if path.name == "region" and path.is_dir():
        return path, world
    for relative in ("region", "dimensions/minecraft/overworld/region"):
        candidate = path / relative
        if candidate.is_dir():
            return candidate, world or path
    return path, world


def world_spawn(data: dict) -> tuple[int, int, int]:
    spawn = data.get("spawn")
    if isinstance(spawn, dict) and "pos" in spawn:
        return tuple(spawn["pos"])
    return data.get("SpawnX", 0), data.get("SpawnY", 0), data.get("SpawnZ", 0)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 1
    return args.run(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bgconvert", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command")
    add_inspect(commands)
    add_convert(commands)
    add_package(commands)
    add_to_mc(commands)
    add_install(commands)
    return parser


def add_inspect(commands) -> None:
    parser = commands.add_parser("inspect", help="report a source world's format and spawn")
    parser.add_argument("world", type=Path, help="world folder or its region folder")
    parser.set_defaults(run=_inspect)


def add_convert(commands) -> None:
    parser = commands.add_parser("convert", help="convert regions into BG region files")
    parser.add_argument("regions", type=Path, help="world folder or its region folder")
    parser.add_argument("out", type=Path, help="output region folder")
    parser.add_argument("--case", default="auto", choices=["auto", *decode.DECODERS])
    parser.add_argument("--shift-x", type=int)
    parser.add_argument("--shift-z", type=int)
    parser.add_argument("--shift-str", type=int, default=0)
    parser.add_argument("--target-x", type=int)
    parser.add_argument("--target-z", type=int)
    parser.set_defaults(run=_convert)


def add_package(commands) -> None:
    parser = commands.add_parser("package", help="assemble a BG map package and its zip")
    parser.add_argument("regions", type=Path, help="converted region folder")
    parser.add_argument("out", type=Path, help="output package folder")
    parser.add_argument("--zip", type=Path, help="output zip (defaults to <out>.zip)")
    parser.add_argument("--icon", type=Path)
    parser.add_argument("--init", type=int, nargs=3, default=[0, 0, 0], metavar=("X", "Y", "Z"))
    parser.add_argument("--birth", type=float, nargs=3, default=[0.0, 0.0, 0.0], metavar=("X", "Y", "Z"))
    parser.set_defaults(run=_package)


def add_to_mc(commands) -> None:
    parser = commands.add_parser("to-mc", help="convert a BG map into a Minecraft 26.3 world")
    parser.add_argument("input", type=Path, help="BG map zip or a folder of r.*.mca files")
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--gamemode", choices=["survival", "creative", "adventure", "spectator"])
    parser.add_argument("--difficulty", choices=["peaceful", "easy", "normal", "hard"])
    parser.add_argument("--spawn", type=int, nargs=3, metavar=("X", "Y", "Z"))
    parser.add_argument("--offset-x", type=int, default=0)
    parser.add_argument("--offset-z", type=int, default=0)
    parser.add_argument("--no-empty-chunks", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.set_defaults(run=_to_mc)


def add_install(commands) -> None:
    parser = commands.add_parser("install", help="push a package into a device slot")
    parser.add_argument("package", type=Path, help="package folder to install")
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--slot", required=True, help="e.g. offi-edit-102")
    parser.add_argument("--id", dest="map_id", required=True, help="slot map id (32 hex)")
    parser.add_argument("--adb", default="adb", help="path to the adb executable")
    parser.add_argument("--serial", help="adb serial, e.g. 127.0.0.1:16384")
    parser.add_argument("--no-stop", action="store_true", help="do not force-stop the game")
    parser.set_defaults(run=_install)


def _inspect(args: argparse.Namespace) -> int:
    region_dir, world = _resolve_world(args.world)
    if not region_dir.is_dir():
        print(f"no region folder at {region_dir}", file=sys.stderr)
        return 2
    data_version = None
    if world is not None and (world / "level.dat").exists():
        data = convert.read_level_data(world)
        data_version = data.get("DataVersion")
        spawn = world_spawn(data)
        print(f"level name: {data.get('LevelName')}")
        print(f"data version: {data_version} ({data.get('Version', {}).get('Name')})")
        print(f"spawn: {spawn[0]} {spawn[1]} {spawn[2]}")
    print(f"detected format: {convert.detect_source_format(region_dir, data_version)}")
    print(f"region files: {len(region.region_files(region_dir))}")
    return 0


def _convert(args: argparse.Namespace) -> int:
    region_dir, world = _resolve_world(args.regions)
    if not region_dir.is_dir():
        print(f"no region folder at {region_dir}", file=sys.stderr)
        return 2
    data_version = None
    if world is not None and (world / "level.dat").exists():
        data_version = convert.read_level_data(world).get("DataVersion")

    shift = _resolve_shift(args, world)
    result = convert.convert_world(region_dir, args.out, shift, args.case, data_version)
    print(f"format: {result.case}")
    print(f"shift: x={shift.x} z={shift.z} str={shift.blocks_y}")
    print(f"chunks written: {result.chunks} (empty skipped: {result.empty})")
    if result.unknown:
        top = ", ".join(f"{name} x{count}" for name, count in result.unknown.most_common(10))
        print(f"unmapped blocks ({len(result.unknown)} kinds): {top}")
    return 0


def _resolve_shift(args: argparse.Namespace, world: Path | None) -> convert.Shift:
    if args.shift_x is not None and args.shift_z is not None:
        return convert.Shift(args.shift_x, args.shift_z, args.shift_str)
    if world is None or not (world / "level.dat").exists():
        raise SystemExit("provide --shift-x/--shift-z or a world folder with level.dat")
    data = convert.read_level_data(world)
    spawn_x, _, spawn_z = world_spawn(data)
    target_x = args.target_x if args.target_x is not None else DEFAULT_TARGET[0]
    target_z = args.target_z if args.target_z is not None else DEFAULT_TARGET[1]
    shift = convert.spawn_shift(spawn_x, spawn_z, target_x, target_z)
    return convert.Shift(shift.x, shift.z, args.shift_str)


def _package(args: argparse.Namespace) -> int:
    zip_path = args.zip or args.out.with_suffix(".zip")
    package.build_package(
        args.regions, args.out, zip_path, args.icon, tuple(args.init), tuple(args.birth)
    )
    files = sum(1 for path in args.out.rglob("*") if path.is_file())
    print(f"package: {args.out} ({files} files)")
    print(f"zip: {zip_path}")
    return 0


def _to_mc(args: argparse.Namespace) -> int:
    argv = [str(args.input)]
    if args.output:
        argv += ["-o", str(args.output)]
    if args.name:
        argv += ["--name", args.name]
    if args.gamemode:
        argv += ["--gamemode", args.gamemode]
    if args.difficulty:
        argv += ["--difficulty", args.difficulty]
    if args.spawn:
        argv += ["--spawn", *(str(value) for value in args.spawn)]
    if args.offset_x:
        argv += ["--offset-x", str(args.offset_x)]
    if args.offset_z:
        argv += ["--offset-z", str(args.offset_z)]
    if args.no_empty_chunks:
        argv.append("--no-empty-chunks")
    if args.force:
        argv.append("--force")
    return bg2mc.main(argv)


def _install(args: argparse.Namespace) -> int:
    adb = install.Adb(args.adb, args.serial or None)
    result = install.install_package(
        adb, args.package, args.zip, args.slot, args.map_id, stop_app=not args.no_stop
    )
    print(f"installed {result.map_id} into {result.slot}")
    print(f"folder files: {result.folder_files} checksum lines: {result.checksum_lines}")
    print(f"zip bytes: {result.zip_bytes}")
    if result.folder_files != result.checksum_lines + 1:
        print("warning: folder files must equal checksum lines + 1", file=sys.stderr)
        return 2
    return 0
