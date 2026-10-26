from collections.abc import Mapping

FALLBACK_BLOCK = (1, 0)
AIR = (0, 0)

COLOURS = {
    "white": 0, "orange": 1, "magenta": 2, "light_blue": 3, "yellow": 4, "lime": 5,
    "pink": 6, "gray": 7, "light_gray": 8, "silver": 8, "cyan": 9, "purple": 10,
    "blue": 11, "brown": 12, "green": 13, "red": 14, "black": 15,
}

WOODS = {
    "oak": 0, "spruce": 1, "birch": 2, "jungle": 3, "acacia": 4, "dark_oak": 5,
    "crimson": 5, "warped": 5, "bamboo": 2, "mangrove": 3, "cherry": 4,
}

WOOD_SLABS = {
    "oak": (126, 125), "spruce": (126, 125), "birch": (126, 125), "jungle": (126, 125),
    "acacia": (126, 125), "dark_oak": (126, 125),
}

WOOD_STAIRS = {
    "oak": 53, "spruce": 134, "birch": 135, "jungle": 136, "acacia": 163, "dark_oak": 164,
    "crimson": 114, "warped": 114, "bamboo": 135, "mangrove": 136, "cherry": 163,
}

WOOD_FENCES = {
    "oak": 85, "spruce": 188, "birch": 189, "jungle": 190, "acacia": 192, "dark_oak": 191,
    "crimson": 85, "warped": 85, "bamboo": 85, "mangrove": 85, "cherry": 85,
}

WOOD_GATES = {
    "oak": 107, "spruce": 183, "birch": 184, "jungle": 185, "acacia": 187, "dark_oak": 186,
    "crimson": 107, "warped": 107, "bamboo": 107, "mangrove": 107, "cherry": 107,
}

WOOD_DOORS = {
    "oak": 64, "iron": 71, "spruce": 193, "birch": 194, "jungle": 195, "acacia": 196,
    "dark_oak": 197, "crimson": 64, "warped": 64, "bamboo": 64, "mangrove": 64, "cherry": 64,
}

STONE_STAIRS = {
    "stone": 67, "cobblestone": 67, "mossy_cobblestone": 67, "stone_brick": 109,
    "mossy_stone_brick": 109, "cracked_stone_brick": 109, "granite": 67, "diorite": 67,
    "andesite": 67, "polished_granite": 67, "polished_diorite": 67, "polished_andesite": 67,
    "brick": 108, "prismarine": 109, "prismarine_brick": 109, "dark_prismarine": 109,
    "nether_brick": 114, "red_nether_brick": 114, "sandstone": 128, "red_sandstone": 180,
    "quartz": 156, "smooth_quartz": 156, "purpur": 203, "end_stone_brick": 109,
    "deepslate_brick": 109, "cobbled_deepslate": 109, "deepslate_tile": 109, "mud_brick": 109,
    "blackstone": 67, "polished_blackstone": 67, "smooth_stone": 67,
}

STONE_SLABS = {
    "stone": 0, "sandstone": 1, "cobblestone": 3, "brick": 4, "stone_brick": 5,
    "nether_brick": 6, "quartz": 7, "smooth_stone": 8, "smooth_sandstone": 9,
    "granite": 0, "diorite": 0, "andesite": 0, "red_nether_brick": 6,
    "mossy_stone_brick": 5, "polished_granite": 0, "polished_diorite": 0,
    "polished_andesite": 0, "prismarine": 7, "prismarine_brick": 7, "dark_prismarine": 7,
    "end_stone_brick": 9, "cut_sandstone": 1, "cut_red_sandstone": -1,
    "smooth_red_sandstone": -1, "deepslate_brick": 0, "cobbled_deepslate": 3,
    "deepslate_tile": 5, "mud_brick": 4, "bamboo_mosaic": 2, "blackstone": 0,
    "smooth_quartz": 7, "mossy_cobblestone": 3,
}

WOOL_SLABS = {
    "white_wool": (44, 7),
    "pink_wool": (205, 0),
    "black_wool": (44, 6),
    "light_gray_wool": (44, 0),
}

COLOR_FAMILIES = {
    "wool": 35, "carpet": 171, "stained_glass": 95, "stained_glass_pane": 160,
    "terracotta": 159, "concrete": 251, "concrete_powder": 252,
}

EXTRA_STAIRS = {
    "smooth_sandstone": 128, "smooth_red_sandstone": 180, "smooth_quartz": 156,
    "blackstone": 67, "polished_blackstone": 67, "mud_brick": 109, "mangrove": 136,
    "cherry": 163, "bamboo": 135, "bamboo_mosaic": 135,
    "white_wool": 156, "pink_wool": 203, "black_wool": 114, "light_gray_wool": 156,
}

TALL_PLANTS = {
    "sunflower": 0, "lilac": 1, "tall_grass": 2, "large_fern": 3, "rose_bush": 4, "peony": 5,
}

SIMPLE = {
    "air": (0, 0), "cave_air": (0, 0), "void_air": (0, 0), "light": (0, 0), "barrier": (166, 0),
    "grass_block": (2, 0), "dirt": (3, 0), "coarse_dirt": (3, 1), "podzol": (3, 2),
    "rooted_dirt": (3, 0), "mycelium": (110, 0), "cobblestone": (4, 0),
    "mossy_cobblestone": (48, 0), "cobbled_deepslate": (4, 0), "bedrock": (7, 0),
    "water": (9, 0), "lava": (11, 0), "gravel": (13, 0), "gold_ore": (14, 0),
    "iron_ore": (15, 0), "coal_ore": (16, 0), "deepslate": (1, 0),
    "deepslate_coal_ore": (16, 0), "deepslate_iron_ore": (15, 0), "deepslate_gold_ore": (14, 0),
    "deepslate_diamond_ore": (56, 0), "deepslate_redstone_ore": (73, 0),
    "deepslate_lapis_ore": (21, 0), "deepslate_copper_ore": (15, 0), "copper_ore": (15, 0),
    "stone": (1, 0), "granite": (1, 1), "polished_granite": (1, 2), "diorite": (1, 3),
    "polished_diorite": (1, 4), "andesite": (1, 5), "polished_andesite": (1, 6), "tuff": (1, 0),
    "calcite": (155, 0), "dripstone_block": (1, 0), "smooth_stone": (1, 0),
    "sulfur_bricks": (159, 4), "tuff_bricks": (98, 2),
    "cracked_nether_bricks": (112, 0),
    "stone_bricks": (98, 0), "cracked_stone_bricks": (98, 2), "chiseled_stone_bricks": (98, 3),
    "mossy_stone_bricks": (98, 1), "infested_stone": (97, 0), "infested_cobblestone": (97, 1),
    "infested_stone_bricks": (97, 2), "infested_mossy_stone_bricks": (97, 3),
    "infested_cracked_stone_bricks": (97, 4), "infested_chiseled_stone_bricks": (97, 5),
    "glass": (20, 0), "tinted_glass": (20, 0), "glass_pane": (102, 0), "lapis_ore": (21, 0),
    "lapis_block": (22, 0), "dispenser": (23, 0), "dropper": (158, 0), "note_block": (25, 0),
    "sand": (12, 0), "red_sand": (12, 1), "repeater": (93, 0), "comparator": (149, 0),
    "redstone_wire": (55, 0), "wet_sponge": (19, 1), "sponge": (19, 0), "gold_block": (41, 0),
    "iron_block": (42, 0), "bricks": (45, 0), "tnt": (46, 0), "bookshelf": (47, 0),
    "obsidian": (49, 0), "crying_obsidian": (49, 0), "torch": (50, 0), "wall_torch": (50, 0),
    "soul_torch": (50, 0), "soul_wall_torch": (50, 0), "redstone_torch": (76, 0),
    "redstone_wall_torch": (76, 0), "lantern": (89, 0), "soul_lantern": (89, 0), "fire": (51, 0),
    "soul_fire": (51, 0), "spawner": (52, 0), "chest": (54, 0), "trapped_chest": (146, 0),
    "ender_chest": (130, 0), "barrel": (54, 0), "crafting_table": (58, 0), "furnace": (61, 0),
    "blast_furnace": (61, 0), "smoker": (61, 0), "farmland": (60, 0), "wheat": (59, 0),
    "carrots": (141, 0), "potatoes": (142, 0), "beetroots": (207, 0), "ladder": (65, 0),
    "rail": (66, 0), "powered_rail": (27, 0), "detector_rail": (28, 0), "activator_rail": (157, 0),
    "lever": (69, 0), "iron_door": (71, 0), "redstone_ore": (73, 0), "lit_redstone_ore": (74, 0),
    "redstone_block": (152, 0), "redstone_lamp": (123, 0), "snow": (78, 0), "snow_block": (80, 0),
    "ice": (79, 0), "frosted_ice": (212, 0), "packed_ice": (174, 0), "blue_ice": (174, 0),
    "cactus": (81, 0), "clay": (82, 0), "jukebox": (84, 0), "netherrack": (87, 0),
    "soul_sand": (88, 0), "soul_soil": (88, 0), "magma_block": (213, 0), "glowstone": (89, 0),
    "shroomlight": (89, 0), "nether_portal": (90, 0), "cake": (92, 0), "brown_mushroom": (39, 0),
    "red_mushroom": (40, 0), "brown_mushroom_block": (99, 0), "red_mushroom_block": (100, 0),
    "iron_bars": (101, 0), "vine": (106, 0), "waterlily": (111, 0), "lily_pad": (111, 0),
    "nether_bricks": (112, 0), "nether_brick_fence": (113, 0), "nether_brick_stairs": (114, 0),
    "nether_wart": (115, 0), "enchanting_table": (116, 0), "brewing_stand": (117, 0),
    "cauldron": (118, 0), "water_cauldron": (118, 0), "lava_cauldron": (118, 0),
    "powder_snow_cauldron": (118, 0), "end_portal": (119, 0), "end_portal_frame": (120, 0),
    "end_stone": (121, 0), "end_stone_bricks": (206, 0), "end_rod": (198, 0),
    "dragon_egg": (122, 0), "redstone_lamp_lit": (124, 0), "sandstone_stairs": (128, 0),
    "emerald_ore": (129, 0), "emerald_block": (133, 0), "tripwire_hook": (131, 0),
    "tripwire": (132, 0), "command_block": (137, 0), "chain_command_block": (211, 0),
    "repeating_command_block": (210, 0), "structure_block": (255, 0), "structure_void": (166, 0),
    "beacon": (138, 0), "cobblestone_wall": (139, 0), "mossy_cobblestone_wall": (139, 1),
    "flower_pot": (140, 0), "anvil": (145, 0), "light_weighted_pressure_plate": (147, 0),
    "heavy_weighted_pressure_plate": (148, 0), "daylight_detector": (151, 0),
    "quartz_ore": (153, 0), "hopper": (154, 0), "quartz_block": (155, 0),
    "chiseled_quartz_block": (155, 1), "quartz_pillar": (155, 2), "quartz_bricks": (155, 1),
    "smooth_quartz": (155, 0), "quartz_stairs": (156, 0), "slime_block": (165, 0),
    "honey_block": (165, 0), "iron_trapdoor": (167, 0), "prismarine": (168, 0),
    "prismarine_bricks": (168, 1), "dark_prismarine": (168, 2), "sea_lantern": (169, 0),
    "hay_block": (170, 0), "bone_block": (216, 0), "nether_wart_block": (214, 0),
    "red_nether_bricks": (215, 0), "red_nether_brick_stairs": (114, 0),
    "red_nether_brick_slab": (44, 6), "purpur_block": (201, 0), "purpur_pillar": (202, 0),
    "purpur_stairs": (203, 0), "chorus_plant": (199, 0), "chorus_flower": (200, 0),
    "dirt_path": (208, 0), "grass_path": (208, 0), "coal_block": (173, 0),
    "diamond_block": (57, 0), "observer": (218, 0), "piston": (33, 0), "sticky_piston": (29, 0),
    "piston_head": (34, 0), "sea_pickle": (9, 0), "kelp": (9, 0), "kelp_plant": (9, 0),
    "seagrass": (9, 0), "tall_seagrass": (9, 0), "bubble_column": (9, 0), "moss_block": (2, 0),
    "moss_carpet": (0, 0), "grass": (31, 1), "fern": (31, 2), "dead_bush": (32, 0),
    "sugar_cane": (83, 0), "melon": (103, 0), "melon_block": (103, 0), "pumpkin": (86, 0),
    "carved_pumpkin": (86, 0), "jack_o_lantern": (91, 0), "brown_mushroom_": (39, 0),
    "bee_nest": (54, 0), "beehive": (54, 0), "amethyst_block": (20, 0),
    "budding_amethyst": (20, 0), "amethyst_cluster": (0, 0), "small_amethyst_bud": (0, 0),
    "medium_amethyst_bud": (0, 0), "large_amethyst_bud": (0, 0), "sculk_sensor": (0, 0),
    "sculk_vein": (0, 0), "sculk": (0, 0), "glow_lichen": (106, 0), "cave_vines": (106, 0),
    "cave_vines_plant": (106, 0), "twisting_vines": (106, 0), "twisting_vines_plant": (106, 0),
    "weeping_vines": (106, 0), "weeping_vines_plant": (106, 0), "nether_sprouts": (0, 0),
    "crimson_roots": (0, 0), "warped_roots": (0, 0), "crimson_fungus": (0, 0),
    "warped_fungus": (0, 0), "spore_blossom": (0, 0), "small_dripleaf": (0, 0),
    "big_dripleaf": (0, 0), "big_dripleaf_stem": (0, 0), "azalea": (18, 0),
    "flowering_azalea": (18, 0), "azalea_leaves": (18, 0), "flowering_azalea_leaves": (18, 0),
    "cherry_leaves": (18, 0), "nether_sprout": (0, 0), "sweet_berry_bush": (0, 0),
    "pointed_dripstone": (1, 0), "crimson_nylium": (87, 0), "warped_nylium": (87, 0),
    "crimson_stem": (17, 0), "warped_stem": (17, 0), "crimson_hyphae": (17, 0),
    "warped_hyphae": (17, 0), "basalt": (1, 0), "smooth_basalt": (1, 0),
    "polished_basalt": (1, 0), "blackstone": (1, 0), "polished_blackstone_button": (77, 0),
    "polished_blackstone_pressure_plate": (70, 0), "packed_mud": (3, 0), "mud": (3, 0),
    "mud_bricks": (45, 0), "torchflower": (0, 0), "pink_petals": (0, 0), "decorated_pot": (0, 0),
    "target": (1, 0), "lightning_rod": (1, 0), "chain": (101, 0), "scaffolding": (0, 0),
    "composter": (54, 0), "grindstone": (1, 0), "stonecutter": (1, 0), "smithing_table": (58, 0),
    "loom": (58, 0), "cartography_table": (58, 0), "fletching_table": (58, 0), "lectern": (47, 0),
    "bell": (0, 0), "campfire": (50, 0), "soul_campfire": (50, 0), "bamboo_sapling": (6, 0),
    "cocoa": (127, 0), "nether_brick_wall": (139, 0), "reinforced_deepslate": (1, 0),
    "large_amethyst_bud_": (0, 0),
}

EXTRA = {
    "diamond_ore": (56, 0), "sandstone": (24, 0), "chiseled_sandstone": (24, 1),
    "cut_sandstone": (24, 2), "smooth_sandstone": (24, 2), "red_sandstone": (179, 0),
    "chiseled_red_sandstone": (179, 1), "cut_red_sandstone": (179, 2),
    "smooth_red_sandstone": (179, 2), "cobweb": (30, 0), "poppy": (38, 0),
    "dandelion": (37, 0), "blue_orchid": (38, 1), "allium": (38, 2), "azure_bluet": (38, 3),
    "red_tulip": (38, 4), "orange_tulip": (38, 5), "white_tulip": (38, 6),
    "pink_tulip": (38, 7), "oxeye_daisy": (38, 8), "cornflower": (38, 2),
    "wither_rose": (38, 0), "raw_iron_block": (42, 0), "raw_gold_block": (41, 0),
    "raw_copper_block": (42, 0), "stone_button": (77, 0), "petrified_oak_slab": (44, 2),
    "mossy_cobblestone_slab": (44, 3), "skeleton_skull": (144, 0),
    "wither_skeleton_skull": (144, 1), "zombie_head": (144, 2), "player_head": (144, 3),
    "creeper_head": (144, 4), "dragon_head": (144, 5), "skeleton_wall_skull": (144, 0),
    "wither_skeleton_wall_skull": (144, 1), "zombie_wall_head": (144, 2),
    "player_wall_head": (144, 3), "creeper_wall_head": (144, 4), "dragon_wall_head": (144, 5),
    "piglin_head": (144, 2), "piglin_wall_head": (144, 2), "candle": (50, 0),
    "white_candle": (50, 0), "smooth_sandstone_stairs": (128, 0),
    "smooth_red_sandstone_stairs": (180, 0), "smooth_quartz_stairs": (156, 0),
    "oak_sign": (63, 0), "spruce_sign": (63, 0), "birch_sign": (63, 0), "jungle_sign": (63, 0),
    "acacia_sign": (63, 0), "dark_oak_sign": (63, 0), "crimson_sign": (63, 0),
    "warped_sign": (63, 0), "oak_wall_sign": (68, 0), "spruce_wall_sign": (68, 0),
    "birch_wall_sign": (68, 0), "jungle_wall_sign": (68, 0), "acacia_wall_sign": (68, 0),
    "dark_oak_wall_sign": (68, 0), "crimson_wall_sign": (68, 0), "warped_wall_sign": (68, 0),
    "oak_hanging_sign": (63, 0), "spruce_hanging_sign": (63, 0), "birch_hanging_sign": (63, 0),
    "jungle_hanging_sign": (63, 0), "acacia_hanging_sign": (63, 0),
    "dark_oak_hanging_sign": (63, 0), "crimson_hanging_sign": (63, 0),
    "warped_hanging_sign": (63, 0), "cherry_hanging_sign": (63, 0),
    "bamboo_hanging_sign": (63, 0), "mangrove_hanging_sign": (63, 0),
    "oak_wall_hanging_sign": (68, 0), "dark_oak_wall_hanging_sign": (68, 0),
    "copper_block": (179, 0), "cut_copper": (179, 0), "exposed_cut_copper": (179, 0),
    "weathered_cut_copper": (179, 0), "oxidized_cut_copper": (179, 0),
    "cut_copper_stairs": (180, 0), "exposed_cut_copper_stairs": (180, 0),
    "weathered_cut_copper_stairs": (180, 0), "oxidized_cut_copper_stairs": (180, 0),
    "waxed_exposed_cut_copper": (179, 0), "waxed_exposed_cut_copper_stairs": (180, 0),
    "waxed_weathered_cut_copper": (179, 0), "cut_copper_slab": (182, 0),
    "exposed_cut_copper_slab": (182, 0), "weathered_cut_copper_slab": (182, 0),
    "oxidized_cut_copper_slab": (182, 0), "bamboo": (0, 0), "bamboo_block": (17, 0),
    "bamboo_mosaic": (5, 2), "bamboo_planks": (5, 2), "mud": (3, 0),
    "grass_block_snow": (2, 0), "terracotta": (172, 0), "stone_pressure_plate": (70, 0),
    "purpur_slab": (205, 0), "red_sandstone_slab": (182, 0), "deepslate_tiles": (98, 0),
    "cracked_deepslate_tiles": (98, 2), "deepslate_bricks": (98, 0),
    "cracked_deepslate_bricks": (98, 2), "chiseled_deepslate": (98, 3),
    "chiseled_nether_bricks": (112, 0), "turtle_egg": (0, 0), "verdant_froglight": (89, 0),
    "mangrove_roots": (17, 0), "powder_snow": (80, 0), "honeycomb_block": (170, 0),
    "chiseled_bookshelf": (47, 0), "purpur_double_slab": (204, 0), "mud_brick": (45, 0),
    "nether_quartz_ore": (153, 0), "dried_kelp_block": (170, 0), "end_gateway": (0, 0),
    "mushroom_stem": (99, 0), "melon_stem": (104, 0), "attached_melon_stem": (104, 0),
    "pumpkin_stem": (105, 0), "attached_pumpkin_stem": (105, 0),
    "chipped_anvil": (145, 1), "damaged_anvil": (145, 2), "lily_of_the_valley": (38, 0),
    "short_grass": (31, 1), "pale_moss_block": (2, 0), "polished_tuff": (1, 0),
    "pale_oak_slab": (126, 0), "pale_oak_planks": (5, 0), "pale_oak_stairs": (53, 0),
}


def resolve(name: str, properties: Mapping[str, str]) -> tuple[int, int] | None:
    block = name.split(":")[-1]

    colour_block = _coloured_block(block)
    if colour_block is not None:
        return colour_block

    wood_block = _wood_block(block, properties)
    if wood_block is not None:
        return wood_block

    if block.endswith("_stairs"):
        base = block[: -len("_stairs")]
        if base in STONE_STAIRS:
            return STONE_STAIRS[base], 0
        if base in EXTRA_STAIRS:
            return EXTRA_STAIRS[base], 0

    if block.endswith("_wall"):
        return 139, 0

    if block.endswith("_slab"):
        slab = _stone_slab(block[: -len("_slab")], properties)
        if slab is not None:
            return slab

    if block in TALL_PLANTS:
        return 175, TALL_PLANTS[block]

    fallback = _generic_fallback(block)
    if fallback is not None:
        return fallback

    if block in EXTRA:
        return EXTRA[block]
    if block in SIMPLE:
        return SIMPLE[block]
    return None


def _coloured_block(block: str) -> tuple[int, int] | None:
    for suffix, base_id in COLOR_FAMILIES.items():
        if block.endswith(f"_{suffix}"):
            colour = block[: -(len(suffix) + 1)]
            if colour in COLOURS:
                return base_id, COLOURS[colour]

    if block.endswith("_glazed_terracotta"):
        colour = block[: -len("_glazed_terracotta")]
        if colour in COLOURS:
            return 235 + COLOURS[colour], 0

    if block.endswith("_shulker_box"):
        colour = block[: -len("_shulker_box")]
        if colour in COLOURS:
            return 219 + COLOURS[colour], 0

    if block == "shulker_box":
        return 219, 0
    if block.endswith("_bed"):
        return 26, 0
    if block.endswith("_banner"):
        return (68, 0) if "wall" in block else (176, 0)
    return None


def _wood_block(block: str, properties: Mapping[str, str]) -> tuple[int, int] | None:
    stripped = block.startswith("stripped_")
    base = block[len("stripped_"):] if stripped else block
    for wood in sorted(WOODS, key=len, reverse=True):
        if not base.startswith(f"{wood}_"):
            continue
        kind = base[len(wood) + 1:]
        index = WOODS[wood]
        if wood == "cherry":
            if kind == "planks":
                return 159, 0
            if kind in ("log", "wood"):
                return 35, 6
        if wood == "crimson" and kind in ("planks", "log", "wood", "stem", "hyphae"):
            return 159, 2
        if wood == "warped" and kind in ("planks", "log", "wood", "stem", "hyphae"):
            return 159, 9
        if kind == "planks" and not stripped:
            return 5, index
        if kind == "sapling":
            return 6, index
        if kind in ("log", "wood", "hyphae", "stem"):
            if wood in ("acacia", "dark_oak"):
                return 162, 0 if wood == "acacia" else 1
            return 17, index
        if kind == "leaves" and not stripped:
            if wood in ("acacia", "dark_oak"):
                return 161, 0 if wood == "acacia" else 1
            return 18, index
        if kind == "slab":
            single, double = WOOD_SLABS.get(wood, (126, 125))
            return (double if properties.get("type") == "double" else single), index
        if kind == "stairs":
            return WOOD_STAIRS[wood], 0
        if kind == "fence":
            return WOOD_FENCES[wood], 0
        if kind == "fence_gate":
            return WOOD_GATES[wood], 0
        if kind == "door":
            return WOOD_DOORS[wood], 0
        if kind == "trapdoor":
            return 96, 0
        if kind == "button":
            return 143, 0
        if kind == "pressure_plate":
            return 72, 0
    return None


def _stone_slab(base: str, properties: Mapping[str, str]) -> tuple[int, int] | None:
    if base == "stone":
        top = 8 if properties.get("type") == "top" else 0
        return (43, 0) if properties.get("type") == "double" else (44, top)
    if base in WOOL_SLABS:
        return WOOL_SLABS[base]
    if base not in STONE_SLABS:
        return None
    data = STONE_SLABS[base]
    if data == -1:
        return 182, 0
    top = 8 if properties.get("type") == "top" else 0
    if properties.get("type") == "double":
        return 43, data
    return 44, data | top


def _generic_fallback(block: str) -> tuple[int, int] | None:
    if block.startswith("dead_") and block.endswith("_coral_block"):
        return 1, 0
    if "coral" in block:
        return (168, 0) if block.endswith("_block") else (0, 0)
    if block.startswith("potted_"):
        return 140, 0
    if block.endswith(("_wall_sign", "_wall_hanging_sign")):
        return 68, 0
    if block.endswith(("_sign", "_hanging_sign")):
        return 63, 0
    if "candle" in block:
        return 50, 0
    if block.endswith(("_head", "_skull")):
        return 144, 0
    if "copper" in block:
        return 179, 0
    return None
