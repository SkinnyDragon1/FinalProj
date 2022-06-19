from typing import Tuple, List

import pygame
import json
from block import Block
from player import Player, default_players

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
# Name colors
BLOCK_COLOR = (89, 78, 77)
FAINT_BLOCK_COLOR = (133, 122, 121)
WARNING_BLOCK_COLOR = (171, 24, 10)
RED_BLOCK_COLOR = (150, 20, 8)

# # Initialize empty json list
json_list = []


def create_block(x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int],
                 warning_color: Tuple[int, int, int]):
    new_block = Block(x1, y1, x2, y2, color)

    for p in default_players:
        if p.box.intersects(new_block.block_box):
            new_block.color = warning_color
            print(warning_color, new_block, p)

    blocks.append(new_block)

    # Set up JSON writing
    new_block_str = [x1, y1, x2, y2, color]

    json_list.append(new_block_str)
    print(json_list)


def draw_blocks():
    # Draw all the blocks on screen
    for block in blocks:
        block.draw(screen)  # Draw block


def draw_faint_block(x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int]):
    tmp_block = Block(x1, y1, x2, y2, color)

    for p in default_players:
        if p.box.intersects(tmp_block.block_box):
            tmp_block = Block(x1, y1, x2, y2, WARNING_BLOCK_COLOR)

    pygame.draw.rect(screen, tmp_block.color, tmp_block.rect, 3)

    pygame.display.update()  # Update the screen


def del_blocks(mouse_pos):
    for block in blocks:
        if block.intersects(mouse_pos):
            blocks.remove(block)


def highlight_blocks(mouse_pos):
    for block in blocks:

        for p in default_players:
            if p.box.intersects(block.block_box):
                if block.intersects(mouse_pos):
                    block.color = WARNING_BLOCK_COLOR
                else:
                    block.color = RED_BLOCK_COLOR
                break
            else:
                if block.intersects(mouse_pos):
                    block.color = FAINT_BLOCK_COLOR
                else:
                    block.color = BLOCK_COLOR


# Update backup
with open("map.json", "r") as f, open("map_backup.json", "w") as t:
    t.write(f.read())

# Loop
running = True
clicked = False
# Initiate while loop
while running:
    screen.fill((0, 0, 0))  # Black

    pos = pygame.mouse.get_pos()  # Track mouse coordinates
    highlight_blocks(pos)
    if clicked:
        draw_blocks()  # Draw all blocks on screen (again so that blocks don't flicker)
        pygame.draw.circle(screen, (255, 0, 0), (block_x1, block_y1), 2)
        pygame.draw.circle(screen, (255, 0, 0), pos, 2)
        draw_faint_block(block_x1, block_y1, pos[0], pos[1], color=FAINT_BLOCK_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            create_block(0, -5, screen.get_width(), -1, BLOCK_COLOR, WARNING_BLOCK_COLOR)  # Create final block at top of screen
            with open('map.json', 'w') as f:
                f.write(json.dumps(json_list))  # Put the json data inside map.json

        pos = pygame.mouse.get_pos()  # Track mouse coordinates

        # Keybind check
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                block_x1, block_y1 = pos
                clicked = True

            elif event.button == 3:
                del_blocks(pos)
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                block_x2, block_y2 = pos
                create_block(block_x1, block_y1, block_x2, block_y2, color=BLOCK_COLOR, warning_color=RED_BLOCK_COLOR)
                clicked = False

    draw_blocks()  # Draw all blocks on screen
    pygame.display.update()  # Update the screen
    pygame.time.Clock().tick(60)  # Limit the game framerate to 60FPS
