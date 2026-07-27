#!/usr/bin/env python3
"""Re-derive each pack's `type` and `genres` so filtering actually works.

The old schema conflated two independent things in one `genre` field, which was
just the folder name. That made "give me fantasy assets" miss every 2D fantasy
pack (they all sat under `2d/`), and made "give me sci-fi" return a bench vice
(the `sci-fi/` folder had collected unrelated industrial props).

Two axes now:

  type    what the asset IS   - 2d, 3d, audio, music, font, material, hdri
  genres  what it DEPICTS     - fantasy, sci-fi, shooter, horror, ...

`genre` and `path` are left alone so folder locations stay stable; `genres` is
the field to filter on.
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TYPE_BY_GENRE = {
    "2d": "2d", "audio": "audio", "music": "music", "fonts": "font",
    "materials": "material", "hdri": "hdri",
}

# theme -> keywords matched against id, title and tags
THEME_KEYWORDS = {
    "fantasy": ["fantasy", "rpg", "medieval", "castle", "dungeon", "knight", "warrior",
                "magic", "ninja", "pirate", "roguelike", "tower defense", "monsters",
                "sword", "potion"],
    "sci-fi": ["sci-fi", "scifi", "space", "alien", "robot", "futuristic", "station",
               "spaceship", "cyborg", "shmup", "synth"],
    # ranged/gun combat only - a sword is "weapons", not "shooter"
    "shooter": ["shooter", "fps", "gun", "guns", "blaster", "military", "ammo",
                "shots", "shmup", "war"],
    "weapons": ["weapon", "weapons", "sword", "blade", "katana", "axe", "bow",
                "firearm", "gun", "combat"],
    "horror": ["horror", "spooky", "halloween", "graveyard", "zombie", "nightmare",
               "creepy", "suspense", "monster"],
    "post-apocalyptic": ["post-apocalyptic", "apocalypse", "wasteland"],
    "western": ["western", "showdown", "cowboy"],
    "prehistoric": ["prehistoric", "dinosaur"],
    "platformer": ["platformer", "sidescroller", "jump"],
    "racing": ["racing", "race", "track", "kart"],
    "puzzle": ["puzzle", "match-3", "boardgame", "cards", "dice", "chess", "casual",
               "arcade", "casino", "slot"],
    "ui": ["ui", "hud", "interface", "buttons", "icons", "menu", "medal", "emoji",
           "controls", "font"],
    "urban": ["city", "building", "town", "street", "road", "furniture", "shop",
              "store", "house", "skyscraper", "commercial", "office", "market",
              "chair", "table", "bed", "cabinet", "shelf", "chandelier", "lighting",
              "couch", "upholstery", "salon", "barber"],
    "nature": ["tree", "trees", "terrain", "rock", "grass", "plant", "farm",
               "landscape", "forest", "outdoor", "nature", "garden", "flower",
               "succulent", "cactus", "leaf", "bush", "moss", "foliage"],
    "industrial": ["workshop", "garage", "warehouse", "factory", "tool", "barrel",
                   "machinery", "construction", "industrial", "laboratory", "lab",
                   "science", "chemistry", "pipe", "scaffold"],
    "vehicles": ["vehicle", "car", "boat", "plane", "train", "ship", "aircraft",
                 "truck", "watercraft", "tram"],
    "characters": ["character", "npc", "people", "animal", "pet", "person"],
    "sports": ["golf", "skate", "football", "soccer", "arena", "sport", "sports",
               "ball", "coaster"],
    "food": ["food", "kitchen", "eat", "coffee", "cheese"],
    "tiles": ["tiles", "tileset", "tile", "hex", "isometric", "modular"],
    "props": ["prop", "props", "box", "crate", "storage", "container", "lantern",
              "camera", "instrument", "furniture", "decorative", "decor", "ornate",
              "lamp", "lighting", "clock", "device", "megaphone", "television",
              "chair", "table", "bed", "cabinet", "shelf"],
}

# Packs the keyword rules get wrong, or that need a theme no keyword implies.
# Value replaces the derived set entirely.
OVERRIDES = {
    # sci-fi/ had collected ordinary industrial props - they are not sci-fi
    "ammo_box": ["industrial", "shooter"],
    "Barrel_01": ["industrial", "props"],
    "Barrel_02": ["industrial", "props"],
    "barrel_03": ["industrial", "props"],
    "barrel_stove": ["industrial", "urban", "props"],
    "bench_vice_01": ["industrial", "props"],
    "bolt_cutters_01": ["industrial", "props"],
    "cardboard_box_01": ["industrial", "props"],
    "chemistry_set": ["industrial", "props"],
    "circuit_board": ["industrial", "props"],
    "classic_laptop": ["urban", "props"],
    "combination_wrench": ["industrial", "props"],
    "concrete_road_barrier": ["urban", "industrial", "props"],
    "concrete_road_barrier_02": ["urban", "industrial", "props"],
    # genuinely sci-fi
    "modular-space-kit": ["sci-fi", "tiles"],
    "space-kit": ["sci-fi", "vehicles"],
    "space-station-kit": ["sci-fi", "tiles"],
    # "monsters"/"marble"/"blaster" keywords mislead on these
    "marble-kit": ["puzzle", "tiles"],
    "cube-pets": ["characters"],
    "mini-characters": ["characters"],
    "blocky-characters": ["characters"],
    "graveyard-kit": ["horror", "characters"],
    "prototype-kit": ["tiles", "characters", "vehicles"],
    "blaster-kit": ["shooter", "sports"],
    "road-textures": ["racing", "urban", "tiles"],
    "parallax-backgrounds": ["nature", "urban"],
    "onscreen-controls": ["ui"],
    "smilies": ["ui"],
    "medals": ["ui"],
    "kenney-pixel-fonts": ["ui"],
    "ui-pack": ["ui"],
    "ui-sounds": ["ui"],
    "jingle-sounds": ["ui"],
    "casino-sounds": ["puzzle"],
    "digital-sounds": ["sci-fi", "ui"],
    "rpg-sounds": ["fantasy"],
}


def normalize(text):
    """Fold punctuation to spaces so a "sci-fi" keyword matches a "sci fi",
    "sci_fi" or "sci-fi" tag. Both sides go through this."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def derive(asset):
    hay = normalize(" ".join([asset["id"], asset["title"]] + asset["tags"]))
    themes = set()
    for theme, words in THEME_KEYWORDS.items():
        if any(re.search(r"\b" + re.escape(normalize(w)) + r"\b", hay) for w in words):
            themes.add(theme)
    return themes


def main():
    path = os.path.join(REPO, "catalog.json")
    with open(path) as fh:
        catalog = json.load(fh)

    for asset in catalog["assets"]:
        asset["type"] = TYPE_BY_GENRE.get(asset["genre"], "3d")
        if asset["id"] in OVERRIDES:
            themes = list(OVERRIDES[asset["id"]])
        else:
            themes = sorted(derive(asset))
        if asset["type"] == "material":
            themes = ["material"]
        elif asset["type"] == "hdri":
            themes = sorted(set(themes) | {"hdri"})
        asset["genres"] = themes or ["misc"]

    with open(path, "w", newline="\r\n") as fh:
        json.dump(catalog, fh, indent=1)

    counts = {}
    for asset in catalog["assets"]:
        for g in asset["genres"]:
            counts[g] = counts.get(g, 0) + 1
    for g, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("  {:<18} {}".format(g, n))
    untagged = [a["id"] for a in catalog["assets"] if a["genres"] == ["misc"]]
    print("untagged:", len(untagged), untagged[:12])


if __name__ == "__main__":
    main(*sys.argv[1:])
