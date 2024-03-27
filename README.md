Required: python tcod
  > pip install tcod

To generate world with biomes:
  > cd worldgen

  > python world-test.py

optionally, provide the world seed (e.g. 11655):
  > python world-test.py 11655

In world-test program:
  * Enter                 => generate new world
  * Left-Click on tile    => display what the biome is
  * Escape                => exit program

---------------------------------

To generate world with biomes & region maps:
  > cd world gen

  > python view.py

optionally, provide the world seed (e.g. 11655):
  > python world-test.py 11655

In world-test program:
  * Enter                             => generate new world
  * Left-Click tile from world map    => enter tile
  * Right-Click while inside tile     => show tiles adjacent to nearest corner of main tile
  * Escape                            => in tile: go back, at world map: exit program
