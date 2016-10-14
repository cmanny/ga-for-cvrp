import os
from PIL import Image

im = Image.new( 'RGB', (250,250), "white") # create a new black image
pixels = im.load() # create the pixel map

with open("data/fruitybun.data", "r") as f:
    content = [line.rstrip("\n") for line in f.readlines()]

dimension = 250
capacity = 500

grid = [list(-1 for _ in range(250)) for _ in range(250)]
grid_demand = [list(-1 for _ in range(250)) for _ in range(250)]
node_map = dict()

for i in range(3, 253):
    node, x, y = [int(x) for x in content[i].split()]
    grid[y][x] = node
    node_map[node] = dict({'x': x, 'y': y})
for i in range(254, 504):
    node, demand = [int(x) for x in content[i].split()]
    grid_demand[node_map[node]['y']][node_map[node]['x']] = demand

for i in range(0, 250):
    for j in range(0, 250):
        pixels[i, j] = (0, 0, grid_demand[i][j]*2) if grid[i][j] != -1 else (0,0,0)
im.show()
