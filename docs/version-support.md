# Version support

The tool has two different version problems. A Minecraft world has to be read
correctly, and a BG map has to be written in a format the target game can open.

## Minecraft to BG

The reader handles these source layouts.

- `.mcr` worlds from Beta and early releases
- old Anvil chunks with numeric block ids
- 1.13 to 1.17 chunks with a local palette
- 1.18 and newer chunks with `sections` and `block_states`
- the 26.3 world layout under `dimensions/minecraft/overworld/region`

The output is always the same legacy Anvil layout that BG uses internally. The
source version does not change the BG side.

## BG to Minecraft

| Target | Path |
| --- | --- |
| 26.3 | built in |
| 1.8.8 to 26.2 | Chunker |
| 1.6.2 and 1.7.10 | not added yet |

Chunker takes the 26.3 world and converts it to the selected target. It also
handles the `level.dat` and block state changes for that version.

## Chunker

Chunker is a Java tool from Hive Games. The project pins version 1.21.0 and
checks the downloaded jar against a SHA-256 hash.

```powershell
bgconvert chunker install
bgconvert chunker status
```

The jar is stored in the user cache. On Windows it is under
`%LOCALAPPDATA%\bg-convert\chunker`. You can override the path with
`--chunker-jar` on `to-mc` or with `BG_CONVERT_CHUNKER_JAR`.

Java 17 or newer is required for the Chunker step. The 26.3 path does not use
Java or Chunker.

## What is lost

This is a terrain converter. It is not a full world import.

- entities are not copied
- chest contents and furnace contents are not copied
- signs are copied by the 26.3 writer when the source has usable sign text
- structures and generated features are not copied
- modded blocks are not known to the block map
- unknown blocks fall back to stone and are reported

World height is also a limit. BG uses Y 0 to 255. A modern world with content
outside that range needs a vertical shift, or that content is lost.

## Tested versions

The current tests cover a small 1.12.2 source and a 26.3 source. I also ran a
BG to 1.20.1 conversion, converted that world back to 26.3, and loaded it in the
26.3 server. It loaded with no errors.

The wider release matrix is still open. See issue #3.
