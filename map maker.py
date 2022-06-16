import pygame
import json
from block import Block

# Initializing Pygame
pygame.init()

# Creating the sceen
screen = pygame.display.set_mode((800, 600))

# Setting up icon and title
pygame.display.set_caption("Map Maker")
icon = pygame.image.load("images/maze_icon.png")
pygame.display.set_icon(icon)

# Set up block coordinates
block_x1 = 0
block_y1 = 0
block_x2 = 0
block_y2 = 0

blocks = []  # Initialize empty block list
BLOCK_COLOR = (89, 78, 77)

# # Initialize empty json list
json_list = []


def create_block(x1, y1, x2, y2, color):

    new_block = Block(x1, y1, x2, y2, color)

    blocks.append(new_block)

    # Set up JSON writing
    new_block_str = [x1, y1, x2, y2, color]

    json_list.append(new_block_str)
    print(json_list)


def draw_blocks():
    # Draw all the blocks on screen
    for block in blocks:
        block.draw(screen)  # Draw block


# Update backup
with open("map.json", "r") as f, open("map_backup.json", "w") as t:
    t.write(f.read())

# Loop
running = True
# Initiate while loop
while running:
    screen.fill((0, 0, 0))  # Black

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            create_block(0, -5, screen.get_width(), -1, BLOCK_COLOR)  # Create final block at top of screen
            with open('map.json', 'w') as f:
                f.write(json.dumps(json_list))  # Put the json data inside map.json

        # Keybind check
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()  # Track mouse coordinates
            block_x1, block_y1 = pos
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()  # Track mouse coordinates
            block_x2, block_y2 = pos
            create_block(block_x1, block_y1, block_x2, block_y2, color=BLOCK_COLOR)

    draw_blocks()  # Draw all blocks on screen
    pygame.display.update()  # Update the screen
    pygame.time.Clock().tick(60)  # Limit the game framerate to 60FPS
