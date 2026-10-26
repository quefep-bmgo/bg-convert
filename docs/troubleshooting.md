# Common problems

## Chunker is not installed

```text
Chunker is not installed. Run `bgconvert chunker install` or pass --chunker-jar.
```

Install the pinned jar once:

```powershell
bgconvert chunker install
```

If the download fails, download `chunker-cli-1.21.0.jar` from the Chunker
release page and pass it directly:

```powershell
bgconvert to-mc map.zip -o world --mc-version 1.20.1 --chunker-jar C:\path\to\chunker-cli-1.21.0.jar
```

## Java was not found

Chunker needs Java 17 or newer. Pass the full path when `java` is not on PATH.

```powershell
bgconvert to-mc map.zip -o world --mc-version 1.20.1 --java "C:\Program Files\Zulu\zulu-25\bin\java.exe"
```

The built in 26.3 writer does not need Java.

## Output already exists

`to-mc` stops before it overwrites a world. Add `--force` when you want to
replace the output.

## A converted map has missing or wrong blocks

Check the conversion output for unknown block ids. BG only has the old block
set, so modern blocks have to be mapped down to the closest block that exists.

## A BG map will not load in a room

The folder name, the checksum file, and the zip have to match. Read the map id
from the game log before installing. The game also removes the folder after it
loads, so extract the package again before opening the same slot.
