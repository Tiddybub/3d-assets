#!/usr/bin/env python3
"""Merge new pack entries into catalog.json and regenerate the README
Contents table and Index from the catalog, so the two never drift apart."""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GENRE_BLURB = {
    "2d": "sprite sheets, tilesets, UI, characters, backgrounds",
    "audio": "sound effect and jingle packs (OGG)",
    "characters": "player sprites, enemies, animals, NPCs",
    "fantasy": "RPG, medieval, dungeon, roguelike, pirate",
    "fonts": "pixel and display fonts (TTF)",
    "hdri": "HDR environment maps for lighting and skyboxes",
    "materials": "seamless PBR textures (colour / normal / roughness / AO)",
    "misc": "everything else",
    "music": "background music tracks by mood (OGG)",
    "modern-urban": "city, town, buildings, roads, furniture",
    "nature": "trees, terrain, rocks, farm, landscape",
    "props": "general-purpose scene props",
    "sci-fi": "space, alien, robot, industrial, futuristic",
    "tiles-terrain": "tilesets, platformer kits, isometric, hex",
    "vehicles": "cars, tanks, ships, planes, racing",
}

CLONING = """## Cloning

The full checkout is about 1.7 GB. Git LFS is **not** used - the repository
exceeded its LFS budget, so large files are stored directly in git. If you only
want the current assets and not the history, a shallow clone is much faster:

```sh
git clone --depth 1 https://github.com/Tiddybub/3d-assets.git
```

To fetch only the packs you need, combine a blobless clone with sparse checkout:

```sh
git clone --filter=blob:none --no-checkout https://github.com/Tiddybub/3d-assets.git
cd 3d-assets
git sparse-checkout set 2d/medieval-fantasy-pack music/fantasy-music audio/rpg-sounds
git checkout
```

"""

THEMES = [
    ("Fantasy / RPG", "fantasy"),
    ("Sci-fi / space", "sci-fi"),
    ("Shooter", "shooter"),
    ("Horror / post-apocalyptic", "horror"),
    ("Western", "western"),
]


def load_new(paths):
    out = []
    for p in paths:
        with open(p) as fh:
            out.extend(json.load(fh))
    return out


def theme_match(asset, theme):
    hay = " ".join(asset["genres"] + asset["tags"]).lower()
    return theme in hay


def main(new_paths):
    with open(REPO + "/catalog.json") as fh:
        catalog = json.load(fh)

    by_id = {a["id"]: a for a in catalog["assets"]}
    order = [a["id"] for a in catalog["assets"]]
    for entry in load_new(new_paths):
        if entry["id"] not in by_id:
            order.insert(0, entry["id"])
        by_id[entry["id"]] = entry

    assets = [by_id[i] for i in order]
    # group by genre so catalog and README share one ordering
    genres = sorted({a["genre"] for a in assets})
    assets = [a for g in genres for a in assets if a["genre"] == g]

    catalog["assets"] = assets
    catalog["packs"] = len(assets)
    with open(REPO + "/catalog.json", "w", newline="\r\n") as fh:
        json.dump(catalog, fh, indent=1)

    # --- README -------------------------------------------------------------
    with open(REPO + "/README.md") as fh:
        readme = fh.read()

    head, _, rest = readme.partition("## Contents\n")
    _, _, tail = rest.partition("## Sources\n")

    counts = {g: sum(1 for a in assets if a["genre"] == g) for g in genres}
    lines = ["## Contents\n\n", "| Genre | Packs | What is in it |\n", "|---|---|---|\n"]
    for g in genres:
        lines.append("| [`{0}/`]({0}/) | {1} | {2} |\n".format(
            g, counts[g], GENRE_BLURB.get(g, "")))

    lines.append("\n## Build a game with these\n\n")
    lines.append("Packs grouped by the themes they suit. Many packs ship a packed "
                 "sprite sheet next to the individual frames.\n\n")
    for label, theme in THEMES:
        hits = [a for a in assets if theme_match(a, theme)]
        lines.append("- **{}** ({} packs): {}\n".format(
            label, len(hits),
            ", ".join("[`{}`]({})".format(a["id"], a["path"]) for a in hits)))
    lines.append("\n" + CLONING + "\n## Index\n\n")

    for g in genres:
        lines.append("### {}\n\n".format(g))
        for a in (x for x in assets if x["genre"] == g):
            lines.append("- [`{id}/`]({path}/) - **{title}** ([source]({src})) - {tags}\n".format(
                id=a["id"], path=a["path"], title=a["title"],
                src=a["source_page"], tags=", ".join(a["tags"])))
        lines.append("\n")

    head = re.sub(r"\*\*\d+ free asset packs\*\*",
                  "**{} free asset packs**".format(len(assets)), head, count=1)

    with open(REPO + "/README.md", "w", newline="\r\n") as fh:
        fh.write(head + "".join(lines) + "## Sources\n" + tail)

    print("packs:", len(assets), "genres:", ", ".join(genres))


if __name__ == "__main__":
    main(sys.argv[1:])
