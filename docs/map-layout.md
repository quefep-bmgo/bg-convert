# Blockman GO map layout

A BG map package is a folder named with the map id. The game also expects a zip
with the same contents next to the folder.

```text
<map-id>/
  checksums.md5
  config.json
  icon.png
  UGCPVPConfig.json
  plugins/
    resources/
      resources.json
  r.x.z.mca
<map-id>.zip
```

The checksum file lists every file except itself. The game compares the file count
against the number of checksum lines. If they do not match it downloads the
original map again.

## Regions

The `.mca` files use the old Anvil layout. A region holds a 32 by 32 group of
chunks. Each chunk has a `Level` compound with `Sections` from Y 0 to 15.

Each section has three important fields.

- `Blocks` is 4096 bytes in X, Z, Y order.
- `Data` is 2048 bytes of four bit metadata values.
- `Y` is the section height, from 0 to 15.

Blockman GO only addresses Y 0 to 255. Taller worlds need a vertical shift or
they lose the parts outside that range.

## Spawn

`config.json` has an `InitPos`, and `UGCPVPConfig.json` has the team birth
positions. The room server still controls the real spawn for an editor slot. The
positions in the package are mostly useful to keep the files in a sane state.

## Replacing a slot

Read the map id from the game log, force stop the game, replace the slot folder
and its zip, then launch the slot again. The game removes the folder after it
loads, so extract the package before every launch if you are testing the same
slot more than once.
