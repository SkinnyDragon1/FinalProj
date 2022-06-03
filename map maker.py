import pygame
import json
from os import getcwd
from shapely.geometry import box

# Initializing Pygame
pygame.init()

# Creating the sceen
screen = pygame.display.set_mode((800, 600))
top_border = 100

# Setting up icon and title
pygame.display.set_caption("Map Maker")
icon = pygame.image.load(f"{getcwd()}/maze_icon.png")
pygame.display.set_icon(icon)

# Set up block coordinates
block_x1 = 0
block_y1 = 0
block_x2 = 0
block_y2 = 0

blocks = []
BLOCK_COLOR = (89, 78, 77)

# Clear json
json_list = []


def create_block(x1, y1, x2, y2, color):
    # global blocks
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1

    width = x2 - x1
    height = y2 - y1
    rect = pygame.Rect(x1, y1, width, height)

    new_block = {"x1": x1,
                 "y1": y1,
                 "x2": x2,
                 "y2": y2,
                 "color": color,
                 "rect": rect
                 }

    blocks.append(new_block)

    # Set up JSON writing
    new_block_str = [x1, y1 + top_border, x2, y2 + top_border, color]

    json_list.append(new_block_str)
    print(json_list)


def draw_blocks():
    for block in blocks:
        pygame.draw.rect(screen, block["color"], block["rect"])  # block[4] --> color; block[5] --> pygame.Rect()


# Update backup
with open("map.json", "r") as f, open("map_backup.json", "w") as t:
    t.write(f.read())

# Loop
running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            create_block(0, -5, screen.get_width(), -1, BLOCK_COLOR)
            with open('map.json', 'w') as f:
                f.write(json.dumps(json_list))

        # Keybind check
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            block_x1, block_y1 = pos
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            block_x2, block_y2 = pos
            create_block(block_x1, block_y1, block_x2, block_y2, color=BLOCK_COLOR)

    draw_blocks()
    pygame.display.update()
    pygame.time.Clock().tick(60)
