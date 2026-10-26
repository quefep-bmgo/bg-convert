import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

APP_ID = "com.sandboxol.blockymods"
BASE_DIR = (
    "/data/media/0/Android/data/com.sandboxol.blockymods/files/Download/SandboxOL/BlockMan/map"
)
STAGE_DIR = "/data/local/tmp/bgconvert"
STAGE_TAR = f"{STAGE_DIR}/package.tar.gz"
STAGE_ZIP = f"{STAGE_DIR}/map.zip"
FILE_OWNER = "u0_a55:ext_data_rw"


@dataclass
class InstallResult:
    slot: str
    map_id: str
    folder_files: int
    checksum_lines: int
    zip_bytes: int


class Adb:
    def __init__(self, executable: str = "adb", serial: str | None = None) -> None:
        self.executable = executable
        self.serial = serial

    def run(self, *args: str, check: bool = True) -> str:
        command = [self.executable]
        if self.serial:
            command += ["-s", self.serial]
        command += list(args)
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if check and result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"command failed: {' '.join(command)}")
        return result.stdout

    def shell(self, script: str, check: bool = True) -> str:
        return self.run("shell", script, check=check)


def force_stop(adb: Adb) -> None:
    adb.shell(f"am force-stop {APP_ID}")


def install_package(
    adb: Adb,
    package_dir: Path,
    zip_path: Path,
    slot: str,
    map_id: str,
    stop_app: bool = True,
) -> InstallResult:
    if stop_app:
        force_stop(adb)

    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "package.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            for path in sorted(package_dir.rglob("*")):
                tar.add(path, arcname=path.relative_to(package_dir).as_posix())
        adb.shell(f"mkdir -p {STAGE_DIR}")
        adb.run("push", str(archive), STAGE_TAR)
        adb.run("push", str(zip_path), STAGE_ZIP)

    target = f"{BASE_DIR}/{slot}/{map_id}"
    adb.shell(f"rm -rf {target}; mkdir -p {target}; tar -xzf {STAGE_TAR} -C {target}")
    adb.shell(f"cp -f {STAGE_ZIP} {BASE_DIR}/{slot}/{map_id}.zip")
    adb.shell(
        f"chown -R {FILE_OWNER} {BASE_DIR}/{slot}; "
        f"chmod 2770 {BASE_DIR}/{slot} {target}; "
        f"find {target} -mindepth 1 -type d -exec chmod 2770 {{}} +; "
        f"find {target} -type f -exec chmod 660 {{}} +; "
        f"chmod 660 {BASE_DIR}/{slot}/{map_id}.zip"
    )

    folder_files = int(adb.shell(f"find {target} -type f | wc -l").strip())
    checksum_lines = int(adb.shell(f"wc -l < {target}/checksums.md5").strip())
    zip_bytes = int(adb.shell(f"stat -c %s {BASE_DIR}/{slot}/{map_id}.zip").strip())
    return InstallResult(slot, map_id, folder_files, checksum_lines, zip_bytes)
