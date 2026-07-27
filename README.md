# 3d-assets

A curated, ready-to-use library of **217 free asset packs** - 3D models, 2D sprites and sprite sheets, tilesets, sound effects, music, fonts, PBR materials and HDRIs. Enough to build complete games without leaving the repo.

**Every asset here is CC0 (public domain equivalent):** free for commercial use, no attribution required, no license tracking needed. Nothing in this repo has usage restrictions.

Assets are sorted into genre folders. Each pack folder holds the original files plus a `SOURCE.md` naming the author, license and original page.

Building something with these? **[AGENTS.md](AGENTS.md)** is the entry point for agents and tooling: repository layout, sprite-sheet atlas formats, and the generated manifests in [`index/`](index/) (`packs.json`, `spritesheets.json`, `audio.json`) that let you query the library without walking 10,000 files.

## Contents

| Genre | Packs | What is in it |
|---|---|---|
| [`2d/`](2d/) | 24 | sprite sheets, tilesets, UI, characters, backgrounds |
| [`audio/`](audio/) | 5 | sound effect and jingle packs (OGG) |
| [`characters/`](characters/) | 7 | player sprites, enemies, animals, NPCs |
| [`fantasy/`](fantasy/) | 7 | RPG, medieval, dungeon, roguelike, pirate |
| [`fonts/`](fonts/) | 1 | pixel and display fonts (TTF) |
| [`hdri/`](hdri/) | 16 | HDR environment maps for lighting and skyboxes |
| [`materials/`](materials/) | 56 | seamless PBR textures (colour / normal / roughness / AO) |
| [`misc/`](misc/) | 7 | everything else |
| [`modern-urban/`](modern-urban/) | 26 | city, town, buildings, roads, furniture |
| [`music/`](music/) | 6 | background music tracks by mood (OGG) |
| [`nature/`](nature/) | 21 | trees, terrain, rocks, farm, landscape |
| [`props/`](props/) | 28 | general-purpose scene props |
| [`sci-fi/`](sci-fi/) | 3 | space, alien, robot, industrial, futuristic |
| [`tiles-terrain/`](tiles-terrain/) | 1 | tilesets, platformer kits, isometric, hex |
| [`vehicles/`](vehicles/) | 9 | cars, tanks, ships, planes, racing |

## Build a game with these

Every pack carries a `genres` list (what it depicts) and a `type` (2d, 3d, audio, music, font, material, hdri). Filter on those, not on the folder - the 2D fantasy packs live in `2d/`, not `fantasy/`. Full lookup: [`index/by-genre.json`](index/by-genre.json).

- **Fantasy / RPG** (16 packs): [`rpg-battle-system`](2d/rpg-battle-system) `2d`, [`ninja-adventure-pack`](2d/ninja-adventure-pack) `2d`, [`medieval-fantasy-pack`](2d/medieval-fantasy-pack) `2d`, [`rpg-pack`](2d/rpg-pack) `2d`, [`rpg-sounds`](audio/rpg-sounds) `audio`, [`superpowers-3d-warriors`](characters/superpowers-3d-warriors) `3d`, [`castle-kit`](fantasy/castle-kit) `3d`, [`fantasy-town-kit`](fantasy/fantasy-town-kit) `3d`, [`mini-dungeon`](fantasy/mini-dungeon) `3d`, [`modular-dungeon-kit`](fantasy/modular-dungeon-kit) `3d`, [`pirate-kit`](fantasy/pirate-kit) `3d`, [`retro-fantasy-kit`](fantasy/retro-fantasy-kit) `3d`, [`tower-defense-kit`](fantasy/tower-defense-kit) `3d`, [`fantasy-music`](music/fantasy-music) `music`, [`antique_estoc`](props/antique_estoc) `3d`, [`antique_katana_01`](props/antique_katana_01) `3d`
- **Sci-fi / space** (9 packs): [`top-down-shooter-pack`](2d/top-down-shooter-pack) `2d`, [`space-shooter-sprites`](2d/space-shooter-sprites) `2d`, [`space-shooter-pack`](2d/space-shooter-pack) `2d`, [`digital-sounds`](audio/digital-sounds) `audio`, [`animated-characters-protagonists`](characters/animated-characters-protagonists) `3d`, [`sci-fi-music`](music/sci-fi-music) `music`, [`modular-space-kit`](sci-fi/modular-space-kit) `3d`, [`space-kit`](sci-fi/space-kit) `3d`, [`space-station-kit`](sci-fi/space-station-kit) `3d`
- **Shooter** (8 packs): [`post-apocalyptic-sprites`](2d/post-apocalyptic-sprites) `2d`, [`western-fps-pack`](2d/western-fps-pack) `2d`, [`top-down-shooter-pack`](2d/top-down-shooter-pack) `2d`, [`space-shooter-sprites`](2d/space-shooter-sprites) `2d`, [`space-shooter-pack`](2d/space-shooter-pack) `2d`, [`blaster-kit`](misc/blaster-kit) `3d`, [`action-music`](music/action-music) `music`, [`ammo_box`](props/ammo_box) `3d`
- **Weapons** (6 packs): [`post-apocalyptic-sprites`](2d/post-apocalyptic-sprites) `2d`, [`western-fps-pack`](2d/western-fps-pack) `2d`, [`top-down-shooter-pack`](2d/top-down-shooter-pack) `2d`, [`action-music`](music/action-music) `music`, [`antique_estoc`](props/antique_estoc) `3d`, [`antique_katana_01`](props/antique_katana_01) `3d`
- **Horror** (4 packs): [`graveyard-kit`](characters/graveyard-kit) `3d`, [`horror-music`](music/horror-music) `music`, [`animated-characters-retro`](nature/animated-characters-retro) `3d`, [`animated-characters-survivors`](nature/animated-characters-survivors) `3d`
- **Post-apocalyptic** (2 packs): [`post-apocalyptic-sprites`](2d/post-apocalyptic-sprites) `2d`, [`horror-music`](music/horror-music) `music`
- **Western** (2 packs): [`western-fps-pack`](2d/western-fps-pack) `2d`, [`western-music`](music/western-music) `music`
- **Platformer** (6 packs): [`prehistoric-platformer-pack`](2d/prehistoric-platformer-pack) `2d`, [`platformer-bricks`](2d/platformer-bricks) `2d`, [`platformer-pack`](2d/platformer-pack) `2d`, [`pixel-platformer-pack`](2d/pixel-platformer-pack) `2d`, [`tappy-plane`](2d/tappy-plane) `2d`, [`platformer-kit`](tiles-terrain/platformer-kit) `3d`
- **Racing** (5 packs): [`road-textures`](2d/road-textures) `2d`, [`coaster-kit`](vehicles/coaster-kit) `3d`, [`racing-kit`](vehicles/racing-kit) `3d`, [`toy-car-kit`](vehicles/toy-car-kit) `3d`, [`train-kit`](vehicles/train-kit) `3d`
- **Puzzle / casual** (6 packs): [`puzzle-pack`](2d/puzzle-pack) `2d`, [`boardgame-pack`](2d/boardgame-pack) `2d`, [`tappy-plane`](2d/tappy-plane) `2d`, [`casino-sounds`](audio/casino-sounds) `audio`, [`mini-arcade`](misc/mini-arcade) `3d`, [`marble-kit`](vehicles/marble-kit) `3d`

## Cloning

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


## Index

### 2d

- [`post-apocalyptic-sprites/`](2d/post-apocalyptic-sprites/) - **Post Apocalyptic Sprites** ([source](https://github.com/doficia/project-cordon-sprites)) - post-apocalyptic, weapons, armor, shooter, items, sprite sheet
- [`parallax-backgrounds/`](2d/parallax-backgrounds/) - **Parallax Backgrounds** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/backgrounds)) - background, parallax, sky, scenery
- [`prehistoric-platformer-pack/`](2d/prehistoric-platformer-pack/) - **Prehistoric Platformer Pack** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/prehistoric-platformer)) - platformer, prehistoric, dinosaur, sidescroller, sprite sheet
- [`western-fps-pack/`](2d/western-fps-pack/) - **Western FPS Pack** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/western-fps-2d)) - shooter, fps, western, weapons, sprite sheet
- [`top-down-shooter-pack/`](2d/top-down-shooter-pack/) - **Top Down Shooter Pack** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/top-down-shooter)) - shooter, top-down, weapons, sci-fi, sprite sheet
- [`space-shooter-sprites/`](2d/space-shooter-sprites/) - **Space Shooter Sprites** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/space-shooter)) - sci-fi, shooter, space, ships, shmup, sprite sheet
- [`rpg-battle-system/`](2d/rpg-battle-system/) - **RPG Battle System** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/rpg-battle-system)) - fantasy, rpg, battle, monsters, turn-based, sprite sheet
- [`ninja-adventure-pack/`](2d/ninja-adventure-pack/) - **Ninja Adventure Pack** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/ninja-adventure)) - fantasy, rpg, ninja, top-down, monsters, sprite sheet
- [`medieval-fantasy-pack/`](2d/medieval-fantasy-pack/) - **Medieval Fantasy Pack** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/medieval-fantasy)) - fantasy, rpg, medieval, monsters, top-down, sprite sheet
- [`smilies/`](2d/smilies/) - **Smilies** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Smilies%20%2825%20assets%29)) - ui, emoji, face, icons
- [`medals/`](2d/medals/) - **Medals** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Medals%20%2830%20assets%29)) - ui, medal, achievement, award
- [`road-textures/`](2d/road-textures/) - **Road Textures** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Road%20textures%20%2880%20assets%29)) - road, tiles, racing, top-down
- [`platformer-bricks/`](2d/platformer-bricks/) - **Platformer Bricks** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Platformer%20bricks%20%28150%20assets%29)) - platformer, tiles, bricks, level
- [`platformer-pack/`](2d/platformer-pack/) - **Platformer Pack** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Platformer%20assets%20%281330%20assets%29)) - platformer, sidescroller, tiles, character, sprites
- [`pixel-platformer-pack/`](2d/pixel-platformer-pack/) - **Pixel Platformer Pack** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Platformer%20assets%20pixel%20%28900%20assets%29)) - pixel art, platformer, tiles, retro, sprites
- [`space-shooter-pack/`](2d/space-shooter-pack/) - **Space Shooter Pack** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Space%20shooter%20assets%20%28300%20assets%29)) - space, shooter, sci-fi, ship, sprites
- [`rpg-pack/`](2d/rpg-pack/) - **RPG Pack** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/RPG%20pack%20%28230%20assets%29)) - rpg, fantasy, top-down, dungeon, tiles
- [`ui-pack/`](2d/ui-pack/) - **UI Pack** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/UI%20pack%20%28220%20assets%29)) - ui, interface, buttons, hud
- [`hexagon-pack/`](2d/hexagon-pack/) - **Hexagon Pack** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Hexagon%20assets%20%28170%20assets%29)) - hex, tiles, strategy, terrain
- [`isometric-roads-pack/`](2d/isometric-roads-pack/) - **Isometric Roads Pack** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Isometric%20road%20assets%20%28140%20assets%29)) - isometric, road, city, tiles
- [`onscreen-controls/`](2d/onscreen-controls/) - **Onscreen Controls** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Onscreen%20controls%20%28400%20assets%29)) - ui, touch, mobile, controls, buttons
- [`puzzle-pack/`](2d/puzzle-pack/) - **Puzzle Pack** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Puzzle%20assets%20%2880%20assets%29)) - puzzle, match-3, casual, sprites
- [`boardgame-pack/`](2d/boardgame-pack/) - **Boardgame Pack** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Boardgame%20pack%20%28480%20assets%29)) - boardgame, cards, dice, chess, tokens
- [`tappy-plane/`](2d/tappy-plane/) - **Tappy Plane** ([source](https://github.com/iwenzhou/kenney/tree/master/Art%20%285190%20files%29/Tappy%20Plane%20%2880%20assets%29)) - plane, flappy, arcade, sidescroller

### audio

- [`casino-sounds/`](audio/casino-sounds/) - **Casino Sounds** ([source](https://github.com/iwenzhou/kenney/tree/master/Audio%20%28295%20files%29/Casino%20sounds%20%2850%20sounds%29)) - sfx, casino, coins, slot
- [`jingle-sounds/`](audio/jingle-sounds/) - **Jingle Sounds** ([source](https://github.com/iwenzhou/kenney/tree/master/Audio%20%28295%20files%29/Jingle%20sounds%20%2885%20sounds%29)) - sfx, jingle, music, stinger
- [`digital-sounds/`](audio/digital-sounds/) - **Digital Sounds** ([source](https://github.com/iwenzhou/kenney/tree/master/Audio%20%28295%20files%29/Digital%20sounds%20%2860%20sounds%29)) - sfx, digital, sci-fi, retro
- [`ui-sounds/`](audio/ui-sounds/) - **UI Sounds** ([source](https://github.com/iwenzhou/kenney/tree/master/Audio%20%28295%20files%29/UI%20sounds%20%2850%20sounds%29)) - sfx, ui, menu, click
- [`rpg-sounds/`](audio/rpg-sounds/) - **RPG Sounds** ([source](https://github.com/iwenzhou/kenney/tree/master/Audio%20%28295%20files%29/RPG%20sounds%20%2850%20sounds%29)) - sfx, rpg, fantasy, combat

### characters

- [`superpowers-3d-warriors/`](characters/superpowers-3d-warriors/) - **Superpowers 3D Warriors** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/3d-warriors)) - character, warrior, fantasy, lowpoly
- [`superpowers-3d-character/`](characters/superpowers-3d-character/) - **Superpowers 3D Character** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/3d-character)) - character, lowpoly, rigged, animated
- [`animated-characters-protagonists/`](characters/animated-characters-protagonists/) - **Animated Characters Protagonists** ([source](https://kenney.nl/assets/animated-characters-protagonists)) - character, criminal, cyborg, skater, skating
- [`blocky-characters/`](characters/blocky-characters/) - **Blocky Characters** ([source](https://kenney.nl/assets/blocky-characters)) - character
- [`cube-pets/`](characters/cube-pets/) - **Cube Pets** ([source](https://kenney.nl/assets/cube-pets)) - animal, cat, dog, pet
- [`graveyard-kit/`](characters/graveyard-kit/) - **Graveyard Kit** ([source](https://kenney.nl/assets/graveyard-kit)) - graveyard, halloween, horror, monster, spooky
- [`mini-characters/`](characters/mini-characters/) - **Mini Characters** ([source](https://kenney.nl/assets/mini-characters)) - character, disability, people

### fantasy

- [`castle-kit/`](fantasy/castle-kit/) - **Castle Kit** ([source](https://kenney.nl/assets/castle-kit)) - castle, medieval
- [`fantasy-town-kit/`](fantasy/fantasy-town-kit/) - **Fantasy Town Kit** ([source](https://kenney.nl/assets/fantasy-town-kit)) - building, medieval, town, wall
- [`mini-dungeon/`](fantasy/mini-dungeon/) - **Mini Dungeon** ([source](https://kenney.nl/assets/mini-dungeon)) - dungeon, medieval, roguelike, rpg
- [`modular-dungeon-kit/`](fantasy/modular-dungeon-kit/) - **Modular Dungeon Kit** ([source](https://kenney.nl/assets/modular-dungeon-kit)) - dungeon, modular, tiles
- [`pirate-kit/`](fantasy/pirate-kit/) - **Pirate Kit** ([source](https://kenney.nl/assets/pirate-kit)) - boat, character, island, pirate, ship, tropical
- [`retro-fantasy-kit/`](fantasy/retro-fantasy-kit/) - **Retro Fantasy Kit** ([source](https://kenney.nl/assets/retro-fantasy-kit)) - building, castle, medieval, retro, town
- [`tower-defense-kit/`](fantasy/tower-defense-kit/) - **Tower Defense Kit** ([source](https://kenney.nl/assets/tower-defense-kit)) - castle, defense, medieval

### fonts

- [`kenney-pixel-fonts/`](fonts/kenney-pixel-fonts/) - **Kenney Pixel Fonts** ([source](https://github.com/iwenzhou/kenney/tree/master/Fonts%20%2810%20files%29)) - font, pixel art, retro, ui

### hdri

- [`aarfontein_dirt_road/`](hdri/aarfontein_dirt_road/) - **Aarfontein Dirt Road** ([source](https://polyhaven.com/a/aarfontein_dirt_road)) - outdoor, nature, natural light, high contrast, clear, morning-afternoon
- [`abandoned_bakery/`](hdri/abandoned_bakery/) - **Abandoned Bakery** ([source](https://polyhaven.com/a/abandoned_bakery)) - natural light, artificial light, urban, indoor, high contrast
- [`abandoned_church/`](hdri/abandoned_church/) - **Abandoned Church** ([source](https://polyhaven.com/a/abandoned_church)) - outdoor, nature, morning-afternoon, partly cloudy, low contrast, natural light
- [`abandoned_construction/`](hdri/abandoned_construction/) - **Abandoned Construction** ([source](https://polyhaven.com/a/abandoned_construction)) - indoor, urban, natural light, medium contrast, overcast
- [`abandoned_factory_canteen_01/`](hdri/abandoned_factory_canteen_01/) - **Abandoned Factory Canteen 01** ([source](https://polyhaven.com/a/abandoned_factory_canteen_01)) - indoor, urban, low contrast, natural light
- [`abandoned_factory_canteen_02/`](hdri/abandoned_factory_canteen_02/) - **Abandoned Factory Canteen 02** ([source](https://polyhaven.com/a/abandoned_factory_canteen_02)) - indoor, urban, natural light, medium contrast
- [`abandoned_games_room_01/`](hdri/abandoned_games_room_01/) - **Abandoned Games Room 01** ([source](https://polyhaven.com/a/abandoned_games_room_01)) - indoor, urban, midday, low contrast, natural light
- [`abandoned_games_room_02/`](hdri/abandoned_games_room_02/) - **Abandoned Games Room 02** ([source](https://polyhaven.com/a/abandoned_games_room_02)) - indoor, urban, midday, low contrast, natural light
- [`abandoned_garage/`](hdri/abandoned_garage/) - **Abandoned Garage** ([source](https://polyhaven.com/a/abandoned_garage)) - indoor, medium contrast, urban, natural light, midday, overcast
- [`abandoned_greenhouse/`](hdri/abandoned_greenhouse/) - **Abandoned Greenhouse** ([source](https://polyhaven.com/a/abandoned_greenhouse)) - low contrast, natural light, indoor, urban, overcast, midday
- [`abandoned_hall_01/`](hdri/abandoned_hall_01/) - **Abandoned Hall 01** ([source](https://polyhaven.com/a/abandoned_hall_01)) - indoor, urban, low contrast, natural light
- [`abandoned_hopper_terminal_01/`](hdri/abandoned_hopper_terminal_01/) - **Abandoned Hopper Terminal 01** ([source](https://polyhaven.com/a/abandoned_hopper_terminal_01)) - outdoor, nature, morning-afternoon, partly cloudy, medium contrast, natural light
- [`abandoned_hopper_terminal_02/`](hdri/abandoned_hopper_terminal_02/) - **Abandoned Hopper Terminal 02** ([source](https://polyhaven.com/a/abandoned_hopper_terminal_02)) - outdoor, nature, morning-afternoon, clear, high contrast, natural light
- [`abandoned_hopper_terminal_03/`](hdri/abandoned_hopper_terminal_03/) - **Abandoned Hopper Terminal 03** ([source](https://polyhaven.com/a/abandoned_hopper_terminal_03)) - outdoor, nature, morning-afternoon, partly cloudy, medium contrast, natural light
- [`abandoned_hopper_terminal_04/`](hdri/abandoned_hopper_terminal_04/) - **Abandoned Hopper Terminal 04** ([source](https://polyhaven.com/a/abandoned_hopper_terminal_04)) - outdoor, nature, midday, clear, high contrast, natural light
- [`abandoned_parking/`](hdri/abandoned_parking/) - **Abandoned Parking** ([source](https://polyhaven.com/a/abandoned_parking)) - outdoor, skies, urban, midday, partly cloudy, high contrast, natural light

### materials

- [`Asphalt023S/`](materials/Asphalt023S/) - **Asphalt023S** ([source](https://ambientcg.com/view?id=Asphalt023S)) - asphalt
- [`Asphalt025C/`](materials/Asphalt025C/) - **Asphalt025C** ([source](https://ambientcg.com/view?id=Asphalt025C)) - asphalt
- [`Asphalt031/`](materials/Asphalt031/) - **Asphalt031** ([source](https://ambientcg.com/view?id=Asphalt031)) - asphalt
- [`Asphalt033/`](materials/Asphalt033/) - **Asphalt033** ([source](https://ambientcg.com/view?id=Asphalt033)) - asphalt
- [`Bricks097/`](materials/Bricks097/) - **Bricks097** ([source](https://ambientcg.com/view?id=Bricks097)) - bricks
- [`Bricks101/`](materials/Bricks101/) - **Bricks101** ([source](https://ambientcg.com/view?id=Bricks101)) - bricks
- [`Bricks102/`](materials/Bricks102/) - **Bricks102** ([source](https://ambientcg.com/view?id=Bricks102)) - bricks
- [`Bricks104/`](materials/Bricks104/) - **Bricks104** ([source](https://ambientcg.com/view?id=Bricks104)) - bricks
- [`Concrete034/`](materials/Concrete034/) - **Concrete034** ([source](https://ambientcg.com/view?id=Concrete034)) - concrete
- [`Concrete046/`](materials/Concrete046/) - **Concrete046** ([source](https://ambientcg.com/view?id=Concrete046)) - concrete
- [`Concrete047A/`](materials/Concrete047A/) - **Concrete047A** ([source](https://ambientcg.com/view?id=Concrete047A)) - concrete
- [`Concrete048/`](materials/Concrete048/) - **Concrete048** ([source](https://ambientcg.com/view?id=Concrete048)) - concrete
- [`Fabric061/`](materials/Fabric061/) - **Fabric061** ([source](https://ambientcg.com/view?id=Fabric061)) - fabric
- [`Fabric066/`](materials/Fabric066/) - **Fabric066** ([source](https://ambientcg.com/view?id=Fabric066)) - fabric
- [`Fabric081C/`](materials/Fabric081C/) - **Fabric081C** ([source](https://ambientcg.com/view?id=Fabric081C)) - fabric
- [`Fabric083/`](materials/Fabric083/) - **Fabric083** ([source](https://ambientcg.com/view?id=Fabric083)) - fabric
- [`Grass001/`](materials/Grass001/) - **Grass001** ([source](https://ambientcg.com/view?id=Grass001)) - grass
- [`Grass004/`](materials/Grass004/) - **Grass004** ([source](https://ambientcg.com/view?id=Grass004)) - grass
- [`Grass005/`](materials/Grass005/) - **Grass005** ([source](https://ambientcg.com/view?id=Grass005)) - grass
- [`Grass008/`](materials/Grass008/) - **Grass008** ([source](https://ambientcg.com/view?id=Grass008)) - grass
- [`Ground037/`](materials/Ground037/) - **Ground037** ([source](https://ambientcg.com/view?id=Ground037)) - ground
- [`Ground054/`](materials/Ground054/) - **Ground054** ([source](https://ambientcg.com/view?id=Ground054)) - ground
- [`Ground068/`](materials/Ground068/) - **Ground068** ([source](https://ambientcg.com/view?id=Ground068)) - ground
- [`Ground103/`](materials/Ground103/) - **Ground103** ([source](https://ambientcg.com/view?id=Ground103)) - ground
- [`Leather026/`](materials/Leather026/) - **Leather026** ([source](https://ambientcg.com/view?id=Leather026)) - leather
- [`Leather030/`](materials/Leather030/) - **Leather030** ([source](https://ambientcg.com/view?id=Leather030)) - leather
- [`Leather037/`](materials/Leather037/) - **Leather037** ([source](https://ambientcg.com/view?id=Leather037)) - leather
- [`Leather038/`](materials/Leather038/) - **Leather038** ([source](https://ambientcg.com/view?id=Leather038)) - leather
- [`Marble006/`](materials/Marble006/) - **Marble006** ([source](https://ambientcg.com/view?id=Marble006)) - marble
- [`Marble012/`](materials/Marble012/) - **Marble012** ([source](https://ambientcg.com/view?id=Marble012)) - marble
- [`Marble016/`](materials/Marble016/) - **Marble016** ([source](https://ambientcg.com/view?id=Marble016)) - marble
- [`Marble021/`](materials/Marble021/) - **Marble021** ([source](https://ambientcg.com/view?id=Marble021)) - marble
- [`Metal046B/`](materials/Metal046B/) - **Metal046B** ([source](https://ambientcg.com/view?id=Metal046B)) - metal
- [`Metal049A/`](materials/Metal049A/) - **Metal049A** ([source](https://ambientcg.com/view?id=Metal049A)) - metal
- [`Metal055A/`](materials/Metal055A/) - **Metal055A** ([source](https://ambientcg.com/view?id=Metal055A)) - metal
- [`Metal063/`](materials/Metal063/) - **Metal063** ([source](https://ambientcg.com/view?id=Metal063)) - metal
- [`PavingStones128/`](materials/PavingStones128/) - **PavingStones128** ([source](https://ambientcg.com/view?id=PavingStones128)) - paving stones
- [`PavingStones138/`](materials/PavingStones138/) - **PavingStones138** ([source](https://ambientcg.com/view?id=PavingStones138)) - paving stones
- [`PavingStones150/`](materials/PavingStones150/) - **PavingStones150** ([source](https://ambientcg.com/view?id=PavingStones150)) - paving stones
- [`PavingStones151/`](materials/PavingStones151/) - **PavingStones151** ([source](https://ambientcg.com/view?id=PavingStones151)) - paving stones
- [`Plaster001/`](materials/Plaster001/) - **Plaster001** ([source](https://ambientcg.com/view?id=Plaster001)) - plaster
- [`Plaster002/`](materials/Plaster002/) - **Plaster002** ([source](https://ambientcg.com/view?id=Plaster002)) - plaster
- [`Plaster003/`](materials/Plaster003/) - **Plaster003** ([source](https://ambientcg.com/view?id=Plaster003)) - plaster
- [`Plaster007/`](materials/Plaster007/) - **Plaster007** ([source](https://ambientcg.com/view?id=Plaster007)) - plaster
- [`Rock051/`](materials/Rock051/) - **Rock051** ([source](https://ambientcg.com/view?id=Rock051)) - rock
- [`Rock058/`](materials/Rock058/) - **Rock058** ([source](https://ambientcg.com/view?id=Rock058)) - rock
- [`Rock063/`](materials/Rock063/) - **Rock063** ([source](https://ambientcg.com/view?id=Rock063)) - rock
- [`Rock064/`](materials/Rock064/) - **Rock064** ([source](https://ambientcg.com/view?id=Rock064)) - rock
- [`Tiles139/`](materials/Tiles139/) - **Tiles139** ([source](https://ambientcg.com/view?id=Tiles139)) - tiles
- [`Tiles140/`](materials/Tiles140/) - **Tiles140** ([source](https://ambientcg.com/view?id=Tiles140)) - tiles
- [`Tiles141/`](materials/Tiles141/) - **Tiles141** ([source](https://ambientcg.com/view?id=Tiles141)) - tiles
- [`Tiles143/`](materials/Tiles143/) - **Tiles143** ([source](https://ambientcg.com/view?id=Tiles143)) - tiles
- [`Wood051/`](materials/Wood051/) - **Wood051** ([source](https://ambientcg.com/view?id=Wood051)) - wood
- [`Wood092/`](materials/Wood092/) - **Wood092** ([source](https://ambientcg.com/view?id=Wood092)) - wood
- [`Wood094/`](materials/Wood094/) - **Wood094** ([source](https://ambientcg.com/view?id=Wood094)) - wood
- [`Wood095/`](materials/Wood095/) - **Wood095** ([source](https://ambientcg.com/view?id=Wood095)) - wood

### misc

- [`blaster-kit/`](misc/blaster-kit/) - **Blaster Kit** ([source](https://kenney.nl/assets/blaster-kit)) - blaster, target, weapon
- [`food-kit/`](misc/food-kit/) - **Food Kit** ([source](https://kenney.nl/assets/food-kit)) - eat, food, kitchen
- [`mini-arcade/`](misc/mini-arcade/) - **Mini Arcade** ([source](https://kenney.nl/assets/mini-arcade)) - arcade, game, machine, play
- [`mini-arena/`](misc/mini-arena/) - **Mini Arena** ([source](https://kenney.nl/assets/mini-arena)) - arena, battle, roman
- [`mini-market/`](misc/mini-market/) - **Mini Market** ([source](https://kenney.nl/assets/mini-market)) - market, shop, store, supermarket
- [`mini-skate/`](misc/mini-skate/) - **Mini Skate** ([source](https://kenney.nl/assets/mini-skate)) - park, skateboard
- [`minigolf-kit/`](misc/minigolf-kit/) - **Minigolf Kit** ([source](https://kenney.nl/assets/minigolf-kit)) - course, golf, level

### modern-urban

- [`3d-road-tiles/`](modern-urban/3d-road-tiles/) - **3D Road Tiles** ([source](https://kenney.nl/assets/3d-road-tiles)) - road, tile
- [`ArmChair_01/`](modern-urban/ArmChair_01/) - **Arm Chair 01** ([source](https://polyhaven.com/a/ArmChair_01)) - gothic, vintage, chair, furniture, victorian, couch, wood, varnished
- [`BarberShopChair_01/`](modern-urban/BarberShopChair_01/) - **Barber Shop Chair 01** ([source](https://polyhaven.com/a/BarberShopChair_01)) - chair, vintage, wood, leather, fancy, upholstery, barber, salon
- [`CashRegister_01/`](modern-urban/CashRegister_01/) - **Cash Register 01** ([source](https://polyhaven.com/a/CashRegister_01)) - commercial, store, vintage, cash, transaction, register, money, sales
- [`Chandelier_01/`](modern-urban/Chandelier_01/) - **Chandelier 01** ([source](https://polyhaven.com/a/Chandelier_01)) - lighting, ceiling, hanging, fixture, chandelier, ornate, vintage
- [`Chandelier_02/`](modern-urban/Chandelier_02/) - **Chandelier 02** ([source](https://polyhaven.com/a/Chandelier_02)) - lighting, ceiling, decorative, chandelier, elegant, hanging, ornate, vintage
- [`Chandelier_03/`](modern-urban/Chandelier_03/) - **Chandelier 03** ([source](https://polyhaven.com/a/Chandelier_03)) - lighting, ceiling, hanging, fixture, chandelier, ornate, decor, elegant
- [`ClassicConsole_01/`](modern-urban/ClassicConsole_01/) - **Classic Console 01** ([source](https://polyhaven.com/a/ClassicConsole_01)) - wood, vintage, table, gothic, victorian, decorative
- [`ClassicNightstand_01/`](modern-urban/ClassicNightstand_01/) - **Classic Nightstand 01** ([source](https://polyhaven.com/a/ClassicNightstand_01)) - wood, vintage, table, gothic, victorian, decorative
- [`CoffeeCart_01/`](modern-urban/CoffeeCart_01/) - **Coffee Cart 01** ([source](https://polyhaven.com/a/CoffeeCart_01)) - table, metal, shelf, plastic, cart, coffee, portable, wheels
- [`CoffeeTable_01/`](modern-urban/CoffeeTable_01/) - **Coffee Table 01** ([source](https://polyhaven.com/a/CoffeeTable_01)) - wood, vintage, table, painted, old, worn, decorative
- [`GothicBed_01/`](modern-urban/GothicBed_01/) - **Gothic Bed 01** ([source](https://polyhaven.com/a/GothicBed_01)) - vintage, gothic, furniture, bed, wood, decorative
- [`GothicCabinet_01/`](modern-urban/GothicCabinet_01/) - **Gothic Cabinet 01** ([source](https://polyhaven.com/a/GothicCabinet_01)) - vintage, wood, gothic, furniture, table, shelf, decorative
- [`GothicCommode_01/`](modern-urban/GothicCommode_01/) - **Gothic Commode 01** ([source](https://polyhaven.com/a/GothicCommode_01)) - vintage, wood, table, gothic, shelf, furniture, decorative
- [`GreenChair_01/`](modern-urban/GreenChair_01/) - **Green Chair 01** ([source](https://polyhaven.com/a/GreenChair_01)) - vintage, wood, gothic, furniture, chair, fabric, decorative
- [`brick-kit/`](modern-urban/brick-kit/) - **Brick Kit** ([source](https://kenney.nl/assets/brick-kit)) - brick, building, plastic, toy
- [`building-kit/`](modern-urban/building-kit/) - **Building Kit** ([source](https://kenney.nl/assets/building-kit)) - building, house, structure
- [`city-kit-commercial/`](modern-urban/city-kit-commercial/) - **City Kit (Commercial)** ([source](https://kenney.nl/assets/city-kit-commercial)) - building, city, skyscraper
- [`city-kit-industrial/`](modern-urban/city-kit-industrial/) - **City Kit (Industrial)** ([source](https://kenney.nl/assets/city-kit-industrial)) - building, city, factory, warehouse
- [`city-kit-roads/`](modern-urban/city-kit-roads/) - **City Kit (Roads)** ([source](https://kenney.nl/assets/city-kit-roads)) - city, road, town
- [`city-kit-suburban/`](modern-urban/city-kit-suburban/) - **City Kit (Suburban)** ([source](https://kenney.nl/assets/city-kit-suburban)) - building, city, suburban
- [`factory-kit/`](modern-urban/factory-kit/) - **Factory Kit** ([source](https://kenney.nl/assets/factory-kit)) - belt, conveyor, factory, industrial, warehouse
- [`furniture-kit/`](modern-urban/furniture-kit/) - **Furniture Kit** ([source](https://kenney.nl/assets/furniture-kit)) - bed, chair, furniture, interior, table
- [`hexagon-kit/`](modern-urban/hexagon-kit/) - **Hexagon Kit** ([source](https://kenney.nl/assets/hexagon-kit)) - building, hexagon, terrain
- [`modular-buildings/`](modern-urban/modular-buildings/) - **Modular Buildings** ([source](https://kenney.nl/assets/modular-buildings)) - building, city, house, modular, town
- [`retro-urban-kit/`](modern-urban/retro-urban-kit/) - **Retro Urban Kit** ([source](https://kenney.nl/assets/retro-urban-kit)) - building, city, retro, urban

### music

- [`loops-and-menu-music/`](music/loops-and-menu-music/) - **Loops and Menu Music** ([source](https://github.com/SoundSafari/CC0-1.0-Music/tree/main/freepd.com)) - music, loop, menu, chiptune, fanfare
- [`western-music/`](music/western-music/) - **Western Music** ([source](https://github.com/SoundSafari/CC0-1.0-Music/tree/main/freepd.com)) - music, western, desert, showdown
- [`horror-music/`](music/horror-music/) - **Horror Music** ([source](https://github.com/SoundSafari/CC0-1.0-Music/tree/main/freepd.com)) - music, horror, suspense, post-apocalyptic, spooky
- [`action-music/`](music/action-music/) - **Action Music** ([source](https://github.com/SoundSafari/CC0-1.0-Music/tree/main/freepd.com)) - music, shooter, action, combat, military, chase
- [`sci-fi-music/`](music/sci-fi-music/) - **Sci-Fi Music** ([source](https://github.com/SoundSafari/CC0-1.0-Music/tree/main/freepd.com)) - music, sci-fi, space, ambient, synth
- [`fantasy-music/`](music/fantasy-music/) - **Fantasy Music** ([source](https://github.com/SoundSafari/CC0-1.0-Music/tree/main/freepd.com)) - music, fantasy, rpg, medieval, epic, boss battle

### nature

- [`animated-characters-retro/`](nature/animated-characters-retro/) - **Animated Characters Retro** ([source](https://kenney.nl/assets/animated-characters-retro)) - character, survival, survivor, zombie
- [`animated-characters-survivors/`](nature/animated-characters-survivors/) - **Animated Characters Survivors** ([source](https://kenney.nl/assets/animated-characters-survivors)) - character, survival, survivor, zombie
- [`anthurium_botany_01/`](nature/anthurium_botany_01/) - **Anthurium Botany 01** ([source](https://polyhaven.com/a/anthurium_botany_01)) - nature, bush, leaf, shrub, leaves, forest, plant, green
- [`bark_debris_01/`](nature/bark_debris_01/) - **Bark Debris 01** ([source](https://polyhaven.com/a/bark_debris_01)) - karoo, desert, dry, dead tree, stick
- [`boulder_01/`](nature/boulder_01/) - **Boulder 01** ([source](https://polyhaven.com/a/boulder_01)) - rocks, boulder, lichen, landscape, rock, geology, formation, weathered
- [`calathea_orbifolia_01/`](nature/calathea_orbifolia_01/) - **Calathea Orbifolia 01** ([source](https://polyhaven.com/a/calathea_orbifolia_01)) - nature, bush, leaf, shrub, green, leaves, forest, plant
- [`celandine_01/`](nature/celandine_01/) - **Celandine 01** ([source](https://polyhaven.com/a/celandine_01)) - field, nature, green, shrub, plant, outdoor, leaf, botany
- [`cheiridopsis_succulent/`](nature/cheiridopsis_succulent/) - **Cheiridopsis Succulent** ([source](https://polyhaven.com/a/cheiridopsis_succulent)) - karoo, desert, south africa, succulent, quartz, tiny, aloe, cactus
- [`coast_land_rocks_02/`](nature/coast_land_rocks_02/) - **Coast Land Rocks 02** ([source](https://polyhaven.com/a/coast_land_rocks_02)) - rocks, coastal, landscape, formation, seaside, shore, geology, pebbles
- [`coast_land_rocks_03/`](nature/coast_land_rocks_03/) - **Coast Land Rocks 03** ([source](https://polyhaven.com/a/coast_land_rocks_03)) - rocks, formation, coastal, landscape, seaside, shore, geology, pebbles
- [`coast_land_rocks_04/`](nature/coast_land_rocks_04/) - **Coast Land Rocks 04** ([source](https://polyhaven.com/a/coast_land_rocks_04)) - landscape, rocks, shore, coastal, geology, shoreline, rock, stones
- [`coast_line_01/`](nature/coast_line_01/) - **Coast Line 01** ([source](https://polyhaven.com/a/coast_line_01)) - coast, shoreline, coastline, seaside, shore, coastal, geology, rock
- [`coast_line_02/`](nature/coast_line_02/) - **Coast Line 02** ([source](https://polyhaven.com/a/coast_line_02)) - landscape, rocks, coastal, rock, shoreline, shore, geology, stones
- [`coast_rocks_01/`](nature/coast_rocks_01/) - **Coast Rocks 01** ([source](https://polyhaven.com/a/coast_rocks_01)) - rocks, seaside, shore, coastal, stones, rock, landscape, geology
- [`coast_rocks_02/`](nature/coast_rocks_02/) - **Coast Rocks 02** ([source](https://polyhaven.com/a/coast_rocks_02)) - seaside, rocks, formation, landscape, shore, geology, coastal, shoreline
- [`coast_rocks_03/`](nature/coast_rocks_03/) - **Coast Rocks 03** ([source](https://polyhaven.com/a/coast_rocks_03)) - rocks, seaside, stones, formation, landscape, shore, rock, shoreline
- [`holiday-kit/`](nature/holiday-kit/) - **Holiday Kit** ([source](https://kenney.nl/assets/holiday-kit)) - cabin, christmas, holiday, tree
- [`mini-forest/`](nature/mini-forest/) - **Mini Forest** ([source](https://kenney.nl/assets/mini-forest)) - archer, base, forest, tent
- [`modular-cave-kit/`](nature/modular-cave-kit/) - **Modular Cave Kit** ([source](https://kenney.nl/assets/modular-cave-kit)) - cave, modular, tiles
- [`nature-kit/`](nature/nature-kit/) - **Nature Kit** ([source](https://kenney.nl/assets/nature-kit)) - foliage, nature, rock, tree
- [`survival-kit/`](nature/survival-kit/) - **Survival Kit** ([source](https://kenney.nl/assets/survival-kit)) - nature, survival

### props

- [`Camera_01/`](props/Camera_01/) - **Camera 01** ([source](https://polyhaven.com/a/Camera_01)) - vintage, camera, antique, ornate, photography, photography, retro, lens
- [`CheeseBox_01/`](props/CheeseBox_01/) - **CheeseBox_01** ([source](https://polyhaven.com/a/CheeseBox_01)) - box, wood, storage, crate, wooden, vintage, farmhouse, aged
- [`Drill_01/`](props/Drill_01/) - **Drill 01** ([source](https://polyhaven.com/a/Drill_01)) - metal, plastic, tool, drill, prop
- [`Lantern_01/`](props/Lantern_01/) - **Lantern 01** ([source](https://polyhaven.com/a/Lantern_01)) - prop, metal, glass, lantern, antique, vintage, hurricane, lamp
- [`Megaphone_01/`](props/Megaphone_01/) - **Megaphone 01** ([source](https://polyhaven.com/a/Megaphone_01)) - plastic, megaphone, device, audio, amplifier, loudspeaker, announcement
- [`Television_01/`](props/Television_01/) - **Television 01** ([source](https://polyhaven.com/a/Television_01)) - vintage, prop, furniture, metal, wood, tv, television, video
- [`Ukulele_01/`](props/Ukulele_01/) - **Ukulele 01** ([source](https://polyhaven.com/a/Ukulele_01)) - instrument, wood, prop, guitar, ukulele, music
- [`WetFloorSign_01/`](props/WetFloorSign_01/) - **Wet Floor Sign 01** ([source](https://polyhaven.com/a/WetFloorSign_01)) - prop, plastic, sign, safety, caution, warning, yellow, hazard
- [`adjustable_wrench/`](props/adjustable_wrench/) - **Adjustable Wrench** ([source](https://polyhaven.com/a/adjustable_wrench)) - vintage, worn, antique, aged, shed, garage, hand tool, rustic
- [`alarm_clock_01/`](props/alarm_clock_01/) - **Alarm Clock 01** ([source](https://polyhaven.com/a/alarm_clock_01)) - clock, time, alarm, bedside, old, 90s, watch, blue
- [`all_purpose_cleaner/`](props/all_purpose_cleaner/) - **All Purpose Cleaner** ([source](https://polyhaven.com/a/all_purpose_cleaner)) - shed, cleaning, home, garage, chemicals, household, janitorial, cleaning supplies
- [`american_football/`](props/american_football/) - **American Football** ([source](https://polyhaven.com/a/american_football)) - game, sports, sport, toy, ball, soccer, football, american
- [`antique_estoc/`](props/antique_estoc/) - **Antique Estoc** ([source](https://polyhaven.com/a/antique_estoc)) - antique, vintage, old, sword, historic, traditional, ornamental, weapon
- [`antique_katana_01/`](props/antique_katana_01/) - **Antique Katana 01** ([source](https://polyhaven.com/a/antique_katana_01)) - antique, ninja, katana, sword, sharp, blade, japanese, weapon
- [`Barrel_01/`](props/Barrel_01/) - **Barrel_01** ([source](https://polyhaven.com/a/Barrel_01)) - barrel, oil, explosive, radioactive, metal, red barrel, oil barrel, drums
- [`Barrel_02/`](props/Barrel_02/) - **Barrel 02** ([source](https://polyhaven.com/a/Barrel_02)) - barrel, water, plastic, garage, warehouse, industrial, storage, drums
- [`ammo_box/`](props/ammo_box/) - **Ammo Box** ([source](https://polyhaven.com/a/ammo_box)) - old, vintage, antique, metal, rusted, army, military, box
- [`barrel_03/`](props/barrel_03/) - **Barrel 03** ([source](https://polyhaven.com/a/barrel_03)) - industrial, barrel, oil, fuel, truck, painted, blue
- [`barrel_stove/`](props/barrel_stove/) - **Barrel Stove** ([source](https://polyhaven.com/a/barrel_stove)) - urban, city, night, fire, heating, outdoor, barrel
- [`bench_vice_01/`](props/bench_vice_01/) - **Bench Vice 01** ([source](https://polyhaven.com/a/bench_vice_01)) - workshop, garage, used, metal, old, shed, woodwork
- [`bolt_cutters_01/`](props/bolt_cutters_01/) - **Bolt Cutters 01** ([source](https://polyhaven.com/a/bolt_cutters_01)) - metal, worn, used, large, workshop, shed, garage
- [`cardboard_box_01/`](props/cardboard_box_01/) - **Cardboard Box 01** ([source](https://polyhaven.com/a/cardboard_box_01)) - warehouse, shed, storage, box, paper, worn, old, broken
- [`chemistry_set/`](props/chemistry_set/) - **Chemistry Set** ([source](https://polyhaven.com/a/chemistry_set)) - laboratory, science, chemistry, glassware, equipment, testing, lab, retort stand
- [`circuit_board/`](props/circuit_board/) - **Circuit Board** ([source](https://polyhaven.com/a/circuit_board)) - computer, components, chip, motherboard, pc hardware, connectors, wiring, power supply
- [`classic_laptop/`](props/classic_laptop/) - **Classic Laptop** ([source](https://polyhaven.com/a/classic_laptop)) - old, vintage, beige, notebook, lcd, trackball
- [`combination_wrench/`](props/combination_wrench/) - **Combination Wrench** ([source](https://polyhaven.com/a/combination_wrench)) - garage, workshop, construction, scratched
- [`concrete_road_barrier/`](props/concrete_road_barrier/) - **Concrete Road Barrier** ([source](https://polyhaven.com/a/concrete_road_barrier)) - road barrier, traffic barrier, safety barrier, wall, road, road block, blockade, partition
- [`concrete_road_barrier_02/`](props/concrete_road_barrier_02/) - **Concrete Road Barrier 02** ([source](https://polyhaven.com/a/concrete_road_barrier_02)) - road barrier, traffic barrier, safety barrier, wall, road, road block, blockade

### sci-fi

- [`modular-space-kit/`](sci-fi/modular-space-kit/) - **Modular Space Kit** ([source](https://kenney.nl/assets/modular-space-kit)) - modular, sci-fi, space, station, tiles
- [`space-kit/`](sci-fi/space-kit/) - **Space Kit** ([source](https://kenney.nl/assets/space-kit)) - planet, ship, space
- [`space-station-kit/`](sci-fi/space-station-kit/) - **Space Station Kit** ([source](https://kenney.nl/assets/space-station-kit)) - interior, sci-fi, space, station

### tiles-terrain

- [`platformer-kit/`](tiles-terrain/platformer-kit/) - **Platformer Kit** ([source](https://kenney.nl/assets/platformer-kit)) - level, oopi, platformer

### vehicles

- [`superpowers-3d-vehicles/`](vehicles/superpowers-3d-vehicles/) - **Superpowers 3D Vehicles** ([source](https://github.com/sparklinlabs/superpowers-asset-packs/tree/master/3d-vehicles)) - vehicle, car, lowpoly
- [`car-kit/`](vehicles/car-kit/) - **Car Kit** ([source](https://kenney.nl/assets/car-kit)) - car, oopi, transportation, vehicle
- [`coaster-kit/`](vehicles/coaster-kit/) - **Coaster Kit** ([source](https://kenney.nl/assets/coaster-kit)) - attraction, coaster, ride, rollercoaster, theme park, track
- [`marble-kit/`](vehicles/marble-kit/) - **Marble Kit** ([source](https://kenney.nl/assets/marble-kit)) - marble, track
- [`prototype-kit/`](vehicles/prototype-kit/) - **Prototype Kit** ([source](https://kenney.nl/assets/prototype-kit)) - animal, building, character, prototype, vehicle, wall, wheelchair
- [`racing-kit/`](vehicles/racing-kit/) - **Racing Kit** ([source](https://kenney.nl/assets/racing-kit)) - car, racing, tile, track, vehicle
- [`toy-car-kit/`](vehicles/toy-car-kit/) - **Toy Car Kit** ([source](https://kenney.nl/assets/toy-car-kit)) - car, toy, track, vehicle
- [`train-kit/`](vehicles/train-kit/) - **Train Kit** ([source](https://kenney.nl/assets/train-kit)) - rail, railroad, track, train, tram, trolley
- [`watercraft-kit/`](vehicles/watercraft-kit/) - **Watercraft Kit** ([source](https://kenney.nl/assets/watercraft-kit)) - boat, ship, vehicle, watercraft

## Sources

- [Kenney](https://kenney.nl) - CC0
- [Poly Haven](https://polyhaven.com) - CC0
- [ambientCG](https://ambientcg.com) - CC0
- [Kenney Asset Pack 1](https://github.com/iwenzhou/kenney) - CC0 (2D packs, mirror of the original Kenney release)
- [Superpowers Asset Packs](https://github.com/sparklinlabs/superpowers-asset-packs) - CC0 (2D game packs and low-poly 3D by Pixel-boy, Sparklin Labs)
- [Project Cordon Sprites](https://github.com/doficia/project-cordon-sprites) - CC0 (community post-apocalyptic item sprites)
- [FreePD](https://freepd.com) via [CC0-1.0-Music](https://github.com/SoundSafari/CC0-1.0-Music) - CC0 (background music)

## Safety

Every archive was scanned before extraction: path-traversal entries, zip bombs and all executable/script file types (`.exe`, `.dll`, `.bat`, `.ps1`, `.js`, `.vbs`, ...) are rejected or stripped. Only art, model, audio, font and text files are committed; the 2D packs additionally had their legacy Flash (`.swf`) sources and `Thumbs.db` files stripped. Poly Haven downloads are additionally verified against the publisher's MD5 checksums.

---

*Generated by the `stock-the-arsenal` skill.*