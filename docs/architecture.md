# Code layout

The package is split by job. The command line module only parses arguments and
calls into the other modules.

| Module | Job |
| --- | --- |
| `cli.py` | arguments, command dispatch, small checks |
| `nbt.py` | read and write the NBT tags used by the old world format |
| `region.py` | read and write `.mcr` and `.mca` region files |
| `model.py` | the small `Chunk` and `Section` values used between steps |
| `decode.py` | turn Minecraft chunk layouts into `Section` values |
| `blocks.py` | map modern block names to the legacy ids BG uses |
| `convert.py` | Minecraft world to BG region files |
| `package.py` | BG folder, checksum file, and zip |
| `bg2mc.py` | BG region files to a Minecraft 26.3 world |
| `legacy_blocks.py` | legacy id and metadata to a 1.18 block state |
| `chunker.py` | install and call the Chunker command line tool |
| `install.py` | copy a package into an Android editor slot |
| `template/` | small BG package files and icon |
| `world_template/` | empty 26.3 world data used by `to-mc` |

## Minecraft to BG

`convert.py` asks `region.py` for each chunk. `decode.py` picks a reader based on
the chunk shape. The reader turns blocks into the small `Section` model. The
writer then puts those sections back into the old `Level` and `Sections` layout
that BG uses. `package.py` copies the BG template and adds the region files,
checksums, and zip.

The block map is intentionally a fallback map. Modern blocks that have no close
old block become stone and are counted in the command output.

## BG to Minecraft

`bg2mc.py` reads the BG region files and writes a 26.3 world. The 26.3 world is
also the handoff point for other versions. When a target below 26.3 is asked for,
`chunker.py` runs Chunker on the finished 26.3 world and writes the final output.

The 26.3 writer keeps the parts that are safe to carry over, including sign text
when the source has it. It drops entities and container contents.

## Adding a version

For a new source layout, add a decoder in `decode.py` and a test. For a new
target below 26.3, first check whether the pinned Chunker release supports it. If
it does, add the version to `SUPPORTED_VERSIONS` in `chunker.py`. If it does not,
the target needs its own writer and level template.
