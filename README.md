# bg-convert

Convert Minecraft Java worlds into Blockman GO map packages.

This is the first working half of the project. It reads a Minecraft world, maps the
blocks to the legacy IDs Blockman GO uses, writes BG region files, and builds the
folder, checksum file, and zip that the game loads.

Blockman GO to Minecraft is not in this branch yet. The version plan is in issue #1.
The map package layout is in [docs/map-layout.md](docs/map-layout.md).

## What works

- `.mcr` and `.mca` worlds
- Beta, 1.2 to 1.12, 1.13 to 1.17, and 1.18 and newer chunk layouts
- horizontal and vertical region shifts
- BG package creation, checksums, and zip output
- adb install into an editor slot

## What does not work

- entities, chest contents, signs, and other block entities
- modded blocks
- Blockman GO to Minecraft
- automatic tests against every Minecraft release

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

The converter has no runtime dependencies.

## Use

Check the source world first.

```powershell
bgconvert inspect "C:\path\to\world"
```

Convert the overworld regions. By default the build is shifted so the world spawn
lands near the BG template spawn at 579, 466. Use `--shift-x` and `--shift-z` when
you want to place it yourself.

```powershell
bgconvert convert "C:\path\to\world" out\regions
```

Build the map package and the zip.

```powershell
bgconvert package out\regions out\my-map --init 579 8 466
```

Install it on a device that already has adb access.

```powershell
bgconvert install out\my-map --zip out\my-map.zip --slot offi-edit-102 --id YOUR_MAP_ID
```

The map id is the 32 character folder name in the game's map slot. Read it from the
game log before you install. The game deletes and re-downloads a slot when the
folder, checksum file, and zip do not match.

## Development

```powershell
pip install -e ".[dev]"
python -m pytest
ruff check .
```
