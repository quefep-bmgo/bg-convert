"""Find, install, and call the Chunker command line tool."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

CHUNKER_VERSION = "1.21.0"
DOWNLOAD_URL = (
    "https://github.com/HiveGamesOSS/Chunker/releases/download/"
    f"{CHUNKER_VERSION}/chunker-cli-{CHUNKER_VERSION}.jar"
)
SHA256 = "63148e587f5ee5a2ca7ebae1079b235c82ae4d1eff8f7a8a8a3398332513dda6"

SUPPORTED_VERSIONS = (
    "1.8.8",
    "1.9",
    "1.9.1",
    "1.9.2",
    "1.9.3",
    "1.9.4",
    "1.10",
    "1.10.1",
    "1.10.2",
    "1.11",
    "1.11.1",
    "1.11.2",
    "1.12",
    "1.12.1",
    "1.12.2",
    "1.13",
    "1.13.1",
    "1.13.2",
    "1.14",
    "1.14.1",
    "1.14.2",
    "1.14.3",
    "1.14.4",
    "1.15",
    "1.15.1",
    "1.15.2",
    "1.16",
    "1.16.1",
    "1.16.2",
    "1.16.3",
    "1.16.4",
    "1.16.5",
    "1.17",
    "1.17.1",
    "1.18",
    "1.18.1",
    "1.18.2",
    "1.19",
    "1.19.1",
    "1.19.2",
    "1.19.3",
    "1.19.4",
    "1.20",
    "1.20.1",
    "1.20.2",
    "1.20.3",
    "1.20.4",
    "1.20.5",
    "1.20.6",
    "1.21",
    "1.21.1",
    "1.21.2",
    "1.21.3",
    "1.21.4",
    "1.21.5",
    "1.21.6",
    "1.21.7",
    "1.21.8",
    "1.21.9",
    "1.21.10",
    "1.21.11",
    "26.1",
    "26.1.1",
    "26.1.2",
    "26.2",
    "26.3",
)

VERSION_FORMATS = {version: "JAVA_" + version.replace(".", "_") for version in SUPPORTED_VERSIONS}


class ChunkerError(RuntimeError):
    pass


def format_name(version: str) -> str:
    try:
        return VERSION_FORMATS[version]
    except KeyError as exc:
        raise ValueError(f"unsupported Minecraft version: {version}") from exc


def default_cache_dir() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return root / "bg-convert" / "chunker" / CHUNKER_VERSION / "chunker-cli.jar"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_jar(explicit: Path | None = None) -> Path:
    if explicit is not None:
        path = Path(explicit)
        if not path.is_file():
            raise ChunkerError(f"Chunker jar not found: {path}")
        return path

    from_env = os.environ.get("BG_CONVERT_CHUNKER_JAR")
    if from_env:
        path = Path(from_env)
        if not path.is_file():
            raise ChunkerError(f"BG_CONVERT_CHUNKER_JAR does not point to a file: {path}")
        return path

    cached = default_cache_dir()
    if cached.is_file():
        if sha256(cached) != SHA256:
            raise ChunkerError(
                "the cached Chunker jar has the wrong checksum. Run `bgconvert chunker install`."
            )
        return cached

    raise ChunkerError(
        "Chunker is not installed. Run `bgconvert chunker install` or pass --chunker-jar."
    )


def install(dest: Path | None = None) -> Path:
    target = Path(dest) if dest is not None else default_cache_dir()
    if target.is_file() and sha256(target) == SHA256:
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(".part")
    request = urllib.request.Request(DOWNLOAD_URL, headers={"User-Agent": "bg-convert"})
    with urllib.request.urlopen(request) as response, partial.open("wb") as file:
        shutil.copyfileobj(response, file)

    if sha256(partial) != SHA256:
        partial.unlink(missing_ok=True)
        raise ChunkerError("the downloaded Chunker jar failed its checksum")

    partial.replace(target)
    return target


def java_version(java: str = "java") -> str:
    try:
        result = subprocess.run(
            [java, "-version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ChunkerError(f"Java was not found: {java}") from exc

    text = result.stderr or result.stdout
    return text.splitlines()[0] if text else "unknown"


def run(
    input_dir: Path,
    output_dir: Path,
    mc_version: str,
    jar: Path | None = None,
    java: str = "java",
) -> None:
    jar_path = resolve_jar(jar)
    target = format_name(mc_version)
    command = [
        java,
        "-jar",
        str(jar_path),
        "-i",
        str(input_dir),
        "-o",
        str(output_dir),
        "-f",
        target,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise ChunkerError(f"Java was not found: {java}") from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise ChunkerError(f"Chunker failed for {mc_version}\n{detail}")
