"""Legacy (<=1.12 numeric-id) Minecraft block -> Minecraft 26.3 block state.

The Blockman GO map bundles use the old Anvil section format:
`Blocks` (byte id), `Data` (nibble metadata) and optionally `Add`.
This module maps a numeric id + metadata pair onto a modern namespaced
block state.  Unknown ids fall back to stone and are reported by the caller.
"""

DYE = [
    "white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
    "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black",
]
PLANK = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak"]
LOG = ["oak", "spruce", "birch", "jungle"]
WOOD_SLAB = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak"]
FLOWER = [
    "poppy", "blue_orchid", "allium", "azure_bluet", "red_tulip",
    "orange_tulip", "white_tulip", "pink_tulip", "oxeye_daisy",
]
STAIR_MAT = {
    53: "oak", 67: "cobblestone", 108: "brick", 109: "stone_brick",
    114: "nether_brick", 128: "sandstone", 134: "spruce", 135: "birch",
    136: "jungle", 163: "acacia", 164: "dark_oak", 180: "red_sandstone",
    203: "purpur",
}
SLAB_MAT = {
    0: ("stone", "stone"),
    1: ("sandstone", "sandstone"),
    2: ("oak", "oak_planks"),
    3: ("cobblestone", "cobblestone"),
    4: ("brick", "bricks"),
    5: ("stone_brick", "stone_bricks"),
    6: ("nether_brick", "nether_bricks"),
    7: ("quartz", "quartz_block"),
}
FACING_STAIRS = ["east", "west", "south", "north"]
FACING_CHEST = ["north", "north", "north", "south", "west", "east"]
FACING_DOOR = ["east", "south", "west", "north"]
FACING_TRAPDOOR = ["south", "north", "east", "west"]
FACING_GATE = ["south", "west", "north", "east"]
FACING_LADDER = {2: "north", 3: "south", 4: "west", 5: "east"}
FACING_TORCH = {1: "east", 2: "west", 3: "south", 4: "north"}
FACING_PISTON = ["down", "up", "north", "south", "west", "east"]
FACING_HOPPER = ["down", "north", "south", "west", "east"]
FACING_OBSERVER = ["down", "up", "north", "south", "west", "east"]
FACING_END_FRAME = ["south", "west", "north", "east"]
FACING_BED = ["south", "west", "north", "east"]


def _st(name, props=None):
    return ("minecraft:" + name, props or {})


def _stairs(mat, data):
    return _st(mat + "_stairs", {
        "facing": FACING_STAIRS[data & 3],
        "half": "top" if data & 4 else "bottom",
        "shape": "straight",
    })


def _slab(mat, data, double=False):
    if double:
        return _st(mat, {})
    return _st(mat + "_slab", {
        "type": "top" if data & 8 else "bottom",
    })


def _door(wood, data):
    return _st(wood + "_door", {
        "facing": FACING_DOOR[data & 3],
        "half": "top" if data & 8 else "bottom",
        "hinge": "right" if data & 16 else "left",
        "open": "true" if data & 4 else "false",
    })


def _trapdoor(wood, data):
    return _st(wood + "_trapdoor", {
        "facing": FACING_TRAPDOOR[data & 3],
        "half": "top" if data & 8 else "bottom",
        "open": "true" if data & 4 else "false",
    })


def _gate(wood, data):
    return _st(wood + "_fence_gate", {
        "facing": FACING_GATE[data & 3],
        "open": "true" if data & 4 else "false",
        "in_wall": "true" if data & 8 else "false",
    })


def _axis(data):
    return {0: "y", 4: "x", 8: "z", 12: "y"}.get(data & 12, "y")


def _log(wood, data):
    if data & 12 == 12:
        return _st(wood + "_wood", {"axis": "y"})
    return _st(wood + "_log", {"axis": _axis(data)})


def _leaves(wood):
    return _st(wood + "_leaves", {"persistent": "true", "distance": "1"})


def _prop(name, value):
    return _st(name, {"properties": value})[0], value  # unused helper


def _even_stairs(name, data):
    return _stairs(name, data)


def _fence(name):
    return _st(name)


def _pane(name):
    return _st(name)


def _wall(name):
    return _st(name)


def _banner(name, data, wall=False):
    if wall:
        return _st("white_wall_banner", {"facing": FACING_STAIRS[data & 3]})
    return _st("white_banner", {"rotation": str(data & 15)})


def _skull(data):
    names = ["skeleton_skull", "wither_skeleton_skull", "zombie_head",
             "player_head", "creeper_head", "dragon_head"]
    return _st(names[data & 7] if (data & 7) < len(names) else "skeleton_skull")


def legacy_state(bid, data):
    """Return (modern_name, properties) or None for air.

    Properties are a dict of strings.  The result is deterministic so it can
    be cached by the converter for every (id, metadata) pair.
    """
    data = int(data) & 15

    if bid == 0:
        return None
    if bid == 1:
        variants = ["stone", "granite", "polished_granite", "diorite",
                    "polished_diorite", "andesite", "polished_andesite"]
        return _st(variants[min(data, 6)])
    if bid == 2:
        return _st("grass_block", {"snowy": "false"})
    if bid == 3:
        return _st("coarse_dirt" if data == 1 else "podzol" if data == 2 else "dirt")
    if bid == 4:
        return _st("cobblestone")
    if bid == 5:
        return _st(PLANK[data % 6] + "_planks")
    if bid == 6:
        return _st(PLANK[data % 6] + "_sapling", {"stage": "0"})
    if bid == 7:
        return _st("bedrock")
    if bid in (8, 9):
        return _st("water", {"level": str(min(data & 7, 7))})
    if bid in (10, 11):
        return _st("lava", {"level": str(min(data & 7, 7))})
    if bid == 12:
        return _st("red_sand" if data == 1 else "sand")
    if bid == 13:
        return _st("gravel")
    if bid == 14:
        return _st("gold_ore")
    if bid == 15:
        return _st("iron_ore")
    if bid == 16:
        return _st("coal_ore")
    if bid == 17:
        return _log(LOG[data % 4], data)
    if bid == 18:
        return _leaves(LOG[data % 4])
    if bid == 19:
        return _st("wet_sponge" if data == 1 else "sponge")
    if bid == 20:
        return _st("glass")
    if bid == 21:
        return _st("lapis_ore")
    if bid == 22:
        return _st("lapis_block")
    if bid == 23:
        return _st("dispenser", {"facing": FACING_PISTON[min(data, 5)]})
    if bid == 24:
        return _st("chiseled_sandstone" if data == 1 else
                   "cut_sandstone" if data == 2 else "sandstone")
    if bid == 25:
        return _st("note_block", {"instrument": "harp", "note": "0", "powered": "false"})
    if bid == 26:
        return _st("red_bed", {
            "facing": FACING_BED[data & 3],
            "part": "head" if data & 8 else "foot",
            "occupied": "true" if data & 4 else "false",
        })
    if bid == 27:
        return _st("powered_rail", {"shape": "north_south", "powered": "false"})
    if bid == 28:
        return _st("detector_rail", {"shape": "north_south", "powered": "false"})
    if bid == 29:
        return _st("sticky_piston", {"facing": FACING_PISTON[min(data, 5)], "extended": "false"})
    if bid == 30:
        return _st("cobweb")
    if bid == 31:
        return _st("dead_bush" if data == 0 else "short_grass" if data == 1 else "fern")
    if bid == 32:
        return _st("dead_bush")
    if bid == 33:
        return _st("piston", {"facing": FACING_PISTON[min(data, 5)], "extended": "false"})
    if bid == 34:
        return _st("piston_head", {"facing": FACING_PISTON[min(data & 7, 5)],
                                   "short": "false", "type": "normal"})
    if bid == 35:
        return _st(DYE[data] + "_wool")
    if bid == 36:
        return None
    if bid == 37:
        return _st("dandelion")
    if bid == 38:
        return _st(FLOWER[data] if data < len(FLOWER) else "poppy")
    if bid == 39:
        return _st("brown_mushroom")
    if bid == 40:
        return _st("red_mushroom")
    if bid == 41:
        return _st("gold_block")
    if bid == 42:
        return _st("iron_block")
    if bid == 43:
        mat, full = SLAB_MAT.get(data & 7, ("stone", "stone"))
        return _st(full)
    if bid == 44:
        mat, _full = SLAB_MAT.get(data & 7, ("stone", "stone"))
        return _slab(mat, data)
    if bid == 45:
        return _st("bricks")
    if bid == 46:
        return _st("tnt")
    if bid == 47:
        return _st("bookshelf")
    if bid == 48:
        return _st("mossy_cobblestone")
    if bid == 49:
        return _st("obsidian")
    if bid == 50:
        if data == 5:
            return _st("torch")
        return _st("wall_torch", {"facing": FACING_TORCH.get(data, "north")})
    if bid == 51:
        return _st("fire", {"age": "0", "east": "false", "north": "false",
                            "south": "false", "up": "false", "west": "false"})
    if bid == 52:
        return _st("spawner")
    if bid == 53:
        return _stairs("oak", data)
    if bid == 54:
        return _st("chest", {"facing": FACING_CHEST[min(data, 5)], "type": "single"})
    if bid == 55:
        return _st("redstone_wire", {"power": "0", "north": "none", "east": "none",
                                     "south": "none", "west": "none"})
    if bid == 56:
        return _st("diamond_ore")
    if bid == 57:
        return _st("diamond_block")
    if bid == 58:
        return _st("crafting_table")
    if bid == 59:
        return _st("wheat", {"age": str(min(data, 7))})
    if bid == 60:
        return _st("farmland", {"moisture": "7"})
    if bid == 61:
        return _st("furnace", {"facing": FACING_CHEST[min(data, 5)], "lit": "false"})
    if bid == 62:
        return _st("furnace", {"facing": FACING_CHEST[min(data, 5)], "lit": "true"})
    if bid == 63:
        return _st("oak_sign", {"rotation": str(data & 15)})
    if bid == 64:
        return _door("oak", data)
    if bid == 65:
        return _st("ladder", {"facing": FACING_LADDER.get(data, "north")})
    if bid == 66:
        return _st("rail", {"shape": "north_south"})
    if bid == 67:
        return _stairs("cobblestone", data)
    if bid == 68:
        return _st("oak_wall_sign", {"facing": FACING_TORCH.get(data, "north")})
    if bid == 69:
        return _st("lever", {"face": "wall", "facing": "north", "powered": "false"})
    if bid == 70:
        return _st("stone_pressure_plate", {"powered": "false"})
    if bid == 71:
        return _door("iron", data)
    if bid == 72:
        return _st("oak_pressure_plate", {"powered": "false"})
    if bid == 73:
        return _st("redstone_ore", {"lit": "false"})
    if bid == 74:
        return _st("redstone_ore", {"lit": "true"})
    if bid == 75:
        return _st("redstone_torch", {"lit": "false"})
    if bid == 76:
        return _st("redstone_wall_torch", {"facing": FACING_TORCH.get(data, "north"),
                                           "lit": "true"})
    if bid == 77:
        return _st("stone_button", {"face": "wall", "facing": "north", "powered": "false"})
    if bid == 78:
        return _st("snow", {"layers": str(min(data + 1, 8))})
    if bid == 79:
        return _st("ice")
    if bid == 80:
        return _st("snow_block")
    if bid == 81:
        return _st("cactus", {"age": "0"})
    if bid == 82:
        return _st("clay")
    if bid == 83:
        return _st("sugar_cane", {"age": "0"})
    if bid == 84:
        return _st("jukebox", {"has_record": "false"})
    if bid == 85:
        return _st("oak_fence")
    if bid == 86:
        return _st("pumpkin")
    if bid == 87:
        return _st("netherrack")
    if bid == 88:
        return _st("soul_sand")
    if bid == 89:
        return _st("glowstone")
    if bid == 90:
        return _st("nether_portal", {"axis": "x"})
    if bid == 91:
        return _st("jack_o_lantern", {"facing": FACING_STAIRS[data & 3]})
    if bid == 92:
        return _st("cake", {"bites": "0"})
    if bid == 93:
        return _st("repeater", {"delay": str((data & 3) + 1),
                                "facing": FACING_STAIRS[(data >> 2) & 3],
                                "locked": "false", "powered": "false"})
    if bid == 94:
        return _st("repeater", {"delay": str((data & 3) + 1),
                                "facing": FACING_STAIRS[(data >> 2) & 3],
                                "locked": "false", "powered": "true"})
    if bid == 95:
        return _st(DYE[data] + "_stained_glass")
    if bid == 96:
        return _trapdoor("oak", data)
    if bid == 97:
        names = ["infested_stone", "infested_cobblestone", "infested_stone_bricks",
                 "infested_mossy_stone_bricks", "infested_cracked_stone_bricks",
                 "infested_chiseled_stone_bricks"]
        return _st(names[min(data, 5)])
    if bid == 98:
        names = ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks",
                 "chiseled_stone_bricks"]
        return _st(names[min(data, 3)])
    if bid == 99:
        return _st("brown_mushroom_block", {"north": "true", "south": "true",
                                            "east": "true", "west": "true",
                                            "up": "true", "down": "true"})
    if bid == 100:
        return _st("red_mushroom_block", {"north": "true", "south": "true",
                                          "east": "true", "west": "true",
                                          "up": "true", "down": "true"})
    if bid == 101:
        return _st("iron_bars")
    if bid == 102:
        return _st("glass_pane")
    if bid == 103:
        return _st("melon")
    if bid == 104:
        return _st("pumpkin_stem", {"age": str(min(data, 7))})
    if bid == 105:
        return _st("melon_stem", {"age": str(min(data, 7))})
    if bid == 106:
        return _st("vine", {"north": "true" if data & 4 else "false",
                            "east": "true" if data & 8 else "false",
                            "south": "true" if data & 1 else "false",
                            "west": "true" if data & 2 else "false",
                            "up": "false"})
    if bid == 107:
        return _gate("oak", data)
    if bid == 108:
        return _stairs("brick", data)
    if bid == 109:
        return _stairs("stone_brick", data)
    if bid == 110:
        return _st("mycelium", {"snowy": "false"})
    if bid == 111:
        return _st("lily_pad")
    if bid == 112:
        return _st("nether_bricks")
    if bid == 113:
        return _st("nether_brick_fence")
    if bid == 114:
        return _stairs("nether_brick", data)
    if bid == 115:
        return _st("nether_wart", {"age": str(min(data, 3))})
    if bid == 116:
        return _st("enchanting_table")
    if bid == 117:
        return _st("brewing_stand", {"has_bottle_0": "false", "has_bottle_1": "false",
                                     "has_bottle_2": "false"})
    if bid == 118:
        return _st("cauldron")
    if bid == 119:
        return _st("end_portal")
    if bid == 120:
        return _st("end_portal_frame", {"eye": "true" if data & 4 else "false",
                                        "facing": FACING_END_FRAME[data & 3]})
    if bid == 121:
        return _st("end_stone")
    if bid == 122:
        return _st("dragon_egg")
    if bid == 123:
        return _st("redstone_lamp", {"lit": "false"})
    if bid == 124:
        return _st("redstone_lamp", {"lit": "true"})
    if bid == 125:
        return _st(WOOD_SLAB[min(data & 7, 5)] + "_planks")
    if bid == 126:
        return _slab(WOOD_SLAB[min(data & 7, 5)], data)
    if bid == 127:
        return _st("cocoa", {"age": str(min(data & 3, 2)), "facing": FACING_TORCH.get(data >> 2, "north")})
    if bid == 128:
        return _stairs("sandstone", data)
    if bid == 129:
        return _st("emerald_ore")
    if bid == 130:
        return _st("ender_chest", {"facing": FACING_CHEST[min(data, 5)], "waterlogged": "false"})
    if bid == 131:
        return _st("tripwire_hook", {"facing": "north", "attached": "false",
                                     "powered": "false"})
    if bid == 132:
        return _st("tripwire", {"attached": "false", "disarmed": "false",
                                "east": "false", "north": "false",
                                "south": "false", "west": "false", "powered": "false"})
    if bid == 133:
        return _st("emerald_block")
    if bid == 134:
        return _stairs("spruce", data)
    if bid == 135:
        return _stairs("birch", data)
    if bid == 136:
        return _stairs("jungle", data)
    if bid == 137:
        return _st("command_block", {"conditional": "false",
                                     "facing": FACING_PISTON[min(data, 5)]})
    if bid == 138:
        return _st("beacon")
    if bid == 139:
        return _st("mossy_cobblestone_wall" if data == 1 else "cobblestone_wall")
    if bid == 140:
        return _st("flower_pot")
    if bid == 141:
        return _st("carrots", {"age": str(min(data, 7))})
    if bid == 142:
        return _st("potatoes", {"age": str(min(data, 7))})
    if bid == 143:
        return _st("oak_button", {"face": "wall", "facing": "north", "powered": "false"})
    if bid == 144:
        return _skull(data)
    if bid == 145:
        return _st("anvil", {"facing": "north"})
    if bid == 146:
        return _st("trapped_chest", {"facing": FACING_CHEST[min(data, 5)], "type": "single"})
    if bid == 147:
        return _st("light_weighted_pressure_plate", {"power": "0"})
    if bid == 148:
        return _st("heavy_weighted_pressure_plate", {"power": "0"})
    if bid == 149:
        return _st("comparator", {"facing": FACING_STAIRS[(data >> 2) & 3],
                                  "mode": "compare", "powered": "false"})
    if bid == 150:
        return _st("comparator", {"facing": FACING_STAIRS[(data >> 2) & 3],
                                  "mode": "compare", "powered": "true"})
    if bid == 151:
        return _st("daylight_detector", {"inverted": "false", "power": str(min(data, 15))})
    if bid == 152:
        return _st("redstone_block")
    if bid == 153:
        return _st("quartz_ore")
    if bid == 154:
        return _st("hopper", {"enabled": "true",
                              "facing": FACING_HOPPER[min(data, 4)]})
    if bid == 155:
        if data == 1:
            return _st("chiseled_quartz_block")
        if data == 2:
            return _st("quartz_pillar", {"axis": _axis(data)})
        return _st("quartz_block")
    if bid == 156:
        return _stairs("quartz", data)
    if bid == 157:
        return _st("activator_rail", {"shape": "north_south", "powered": "false"})
    if bid == 158:
        return _st("dropper", {"facing": FACING_PISTON[min(data, 5)], "triggered": "false"})
    if bid == 159:
        return _st(DYE[data] + "_terracotta")
    if bid == 160:
        return _st(DYE[data] + "_stained_glass_pane")
    if bid == 161:
        wood = "dark_oak" if data & 1 else "acacia"
        return _leaves(wood)
    if bid == 162:
        wood = "dark_oak" if data & 1 else "acacia"
        return _log(wood, data)
    if bid == 163:
        return _stairs("acacia", data)
    if bid == 164:
        return _stairs("dark_oak", data)
    if bid == 165:
        return _st("slime_block")
    if bid == 166:
        return _st("barrier")
    if bid == 167:
        return _st("iron_trapdoor", {"facing": FACING_TRAPDOOR[data & 3],
                                     "half": "top" if data & 8 else "bottom",
                                     "open": "true" if data & 4 else "false"})
    if bid == 168:
        names = ["prismarine", "prismarine_bricks", "dark_prismarine"]
        return _st(names[min(data, 2)])
    if bid == 169:
        return _st("sea_lantern")
    if bid == 170:
        return _st("hay_block", {"axis": _axis(data)})
    if bid == 171:
        return _st(DYE[data] + "_carpet")
    if bid == 172:
        return _st("terracotta")
    if bid == 173:
        return _st("coal_block")
    if bid == 174:
        return _st("packed_ice")
    if bid == 175:
        plants = ["sunflower", "lilac", "tall_grass", "large_fern",
                  "rose_bush", "peony"]
        plant = plants[data & 7] if (data & 7) < len(plants) else "tall_grass"
        return _st(plant, {"half": "upper" if data & 8 else "lower"})
    if bid == 176:
        return _banner("white", data, wall=False)
    if bid == 177:
        return _banner("white", data, wall=True)
    if bid == 178:
        return _st("daylight_detector", {"inverted": "true", "power": str(min(data, 15))})
    if bid == 179:
        return _st("chiseled_red_sandstone" if data == 1 else
                   "cut_red_sandstone" if data == 2 else "red_sandstone")
    if bid == 180:
        return _stairs("red_sandstone", data)
    if bid == 181:
        return _st("red_sandstone")
    if bid == 182:
        return _slab("red_sandstone", data)
    if bid == 183:
        return _gate("spruce", data)
    if bid == 184:
        return _gate("birch", data)
    if bid == 185:
        return _gate("jungle", data)
    if bid == 186:
        return _gate("dark_oak", data)
    if bid == 187:
        return _gate("acacia", data)
    if bid == 188:
        return _st("spruce_fence")
    if bid == 189:
        return _st("birch_fence")
    if bid == 190:
        return _st("jungle_fence")
    if bid == 191:
        return _st("dark_oak_fence")
    if bid == 192:
        return _st("acacia_fence")
    if bid == 193:
        return _door("spruce", data)
    if bid == 194:
        return _door("birch", data)
    if bid == 195:
        return _door("jungle", data)
    if bid == 196:
        return _door("acacia", data)
    if bid == 197:
        return _door("dark_oak", data)
    if bid == 198:
        return _st("end_rod", {"facing": FACING_PISTON[min(data, 5)]})
    if bid == 199:
        return _st("chorus_plant", {"north": "true", "south": "true",
                                    "east": "true", "west": "true",
                                    "up": "true", "down": "true"})
    if bid == 200:
        return _st("chorus_flower", {"age": "0"})
    if bid == 201:
        return _st("purpur_block")
    if bid == 202:
        return _st("purpur_pillar", {"axis": _axis(data)})
    if bid == 203:
        return _stairs("purpur", data)
    if bid == 204:
        return _st("purpur_block")
    if bid == 205:
        return _slab("purpur", data)
    if bid == 206:
        return _st("end_stone_bricks")
    if bid == 207:
        return _st("beetroots", {"age": str(min(data, 3))})
    if bid == 208:
        return _st("dirt_path")
    if bid == 209:
        return _st("end_gateway")
    if bid == 210:
        return _st("repeating_command_block", {"conditional": "false",
                                                "facing": FACING_PISTON[min(data, 5)]})
    if bid == 211:
        return _st("chain_command_block", {"conditional": "false",
                                           "facing": FACING_PISTON[min(data, 5)]})
    if bid == 212:
        return _st("frosted_ice", {"age": "0"})
    if bid == 213:
        return _st("magma_block")
    if bid == 214:
        return _st("nether_wart_block")
    if bid == 215:
        return _st("red_nether_bricks")
    if bid == 216:
        return _st("bone_block", {"axis": _axis(data)})
    if bid == 217:
        return _st("structure_block", {"mode": "save"})
    if bid == 218:
        return _st("observer", {"facing": FACING_OBSERVER[min(data, 5)], "powered": "false"})
    if 219 <= bid <= 234:
        return _st(DYE[bid - 219] + "_shulker_box", {"facing": "up"})
    if 235 <= bid <= 250:
        return _st(DYE[bid - 235] + "_glazed_terracotta",
                   {"facing": FACING_STAIRS[data & 3]})
    if bid == 251:
        return _st(DYE[data] + "_concrete")
    if bid == 252:
        return _st(DYE[data] + "_concrete_powder")
    if bid == 255:
        return _st("structure_void")

    # Unknown legacy id: keep the map solid rather than punching holes.
    return _st("stone")


LEGACY_TABLE = [legacy_state(bid, data) for bid in range(256) for data in range(16)]


def state_for(bid, data):
    if bid < 0 or bid > 255:
        return LEGACY_TABLE[1 * 16]  # stone
    return LEGACY_TABLE[(bid << 4) | (data & 15)]
