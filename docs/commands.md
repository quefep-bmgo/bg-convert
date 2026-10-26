# Command reference

## inspect

```text
bgconvert inspect <world>
```

Prints the level name, data version, spawn, chunk format, and region count. The
path can be a world folder, a `region` folder, or the 26.3 dimensions region
folder.

## convert

```text
bgconvert convert <world> <out> [options]
```

Writes BG region files from a Minecraft world.

Options:

- `--case auto|modern|paletted|legacy|beta` overrides format detection
- `--shift-x` and `--shift-z` move the map by whole chunks
- `--shift-str` moves the map vertically
- `--target-x` and `--target-z` shift the world spawn to that point

The default target is 579 by 466, the spawn used by the BG template.

## package

```text
bgconvert package <regions> <out> [options]
```

Builds the BG folder, checksum file, and zip.

Options:

- `--zip` sets the zip path
- `--icon` sets the map icon
- `--init X Y Z` sets `InitPos`
- `--birth X Y Z` sets the first birth position

## to-mc

```text
bgconvert to-mc <map> -o <world> [options]
```

Writes a Minecraft Java world from a BG map zip or a folder of region files.

Options:

- `--mc-version` defaults to 26.3 and accepts 1.8.8 through 26.3
- `--gamemode` accepts survival, creative, adventure, or spectator
- `--difficulty` accepts peaceful, easy, normal, or hard
- `--spawn X Y Z` overrides the computed spawn
- `--offset-x` and `--offset-z` move the map by whole chunks
- `--no-empty-chunks` skips the empty chunks inside the source region area
- `--chunker-jar` points at a Chunker jar
- `--java` points at the Java executable
- `--force` replaces an existing output

Targets below 26.3 need Chunker and Java 17 or newer. Use `chunker install` once.
If the output ends in `.zip`, the tool writes a zipped world.

## chunker

```text
bgconvert chunker install [--dest PATH]
bgconvert chunker status
```

`install` downloads the pinned Chunker jar and checks its SHA-256. `status` shows
the supported version range, Java, the cache path, and the jar hash.

## install

```text
bgconvert install <package> --zip <zip> --slot <slot> --id <map-id> [options]
```

Copies a BG package into an editor slot with adb.

Options:

- `--adb` sets the adb executable
- `--serial` sets the device serial
- `--no-stop` skips the force stop

Read the map id from the game log. The slot folder and zip name must match.
