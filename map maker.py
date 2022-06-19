from typing import Tuple

import pygame
import json
from block import Block
from player import default_players

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


def create_block(x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int], warning_color: Tuple[int, int, int]):

    new_block = Block(x1, y1, x2, y2, color)

    for p in default_players:  # Loop over players
        if p.box.intersects(new_block.block_box):  # If box is intersecting with player's box
            new_block.color = warning_color  # Set new color

    blocks.append(new_block)

def blocks_to_json() -> None:
    create_block(0, -5, screen.get_width(), -1, BLOCK_COLOR, WARNING_BLOCK_COLOR)  # Create final block at top of screen

    for block in blocks:
        # Set up JSON writing
        new_block_str = [block.x1, block.y1, block.x2, block.y2, BLOCK_COLOR]

        json_list.append(new_block_str)

    with open('map.json', 'w') as file:
        file.write(json.dumps(json_list))  # Put the json data inside map.json


def draw_blocks() -> None:
    # Draw all the blocks on screen
    for block in blocks:
        block.draw(screen)  # Draw block


def draw_faint_block(x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int]) -> None:
    tmp_block = Block(x1, y1, x2, y2, color)

    for p in default_players:  # Loop over players
        if p.box.intersects(tmp_block.block_box): # If block is touching player's box
            tmp_block.color = WARNING_BLOCK_COLOR  # Change block color

    pygame.draw.rect(screen, tmp_block.color, tmp_block.rect, 3)  # Draw a rectangle with a 3 pixel border

    pygame.display.update()  # Update the screen


def del_blocks(mouse_pos) -> None:
    for block in blocks[::-1]:  # Start from topmost block
        if block.intersects(mouse_pos):  # If block is touching mouse
            blocks.remove(block)  # Delete block
            break  # Stop looping


def highlight_blocks(mouse_pos) -> None:
    for block in blocks:  # Loop over all blocks
        for p in default_players:  # Loop over players
            if p.box.intersects(block.block_box):  # If block is touching player's box
                if block.intersects(mouse_pos):  # If block is touching mouse
                    block.color = WARNING_BLOCK_COLOR  # Highlighted red block
                else:
                    block.color = RED_BLOCK_COLOR  # Normal red block
                break
            else:
                if block.intersects(mouse_pos):
                    block.color = FAINT_BLOCK_COLOR  # Highlighted block
                else:
                    block.color = BLOCK_COLOR  # Normal block


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
        pygame.draw.circle(screen, (255, 0, 0), (block_x1, block_y1), 2)  # Draw red circle indicator for corner
        pygame.draw.circle(screen, (255, 0, 0), pos, 2)  # Draw red circle indicator for corner
        draw_faint_block(block_x1, block_y1, pos[0], pos[1], color=FAINT_BLOCK_COLOR)  # Draw rectangle outline

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            blocks_to_json()  # Convert final block list to json format
            running = False

        pos = pygame.mouse.get_pos()  # Track mouse coordinates

        # Keybind check
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left clock
                block_x1, block_y1 = pos  # Track mouse position
                clicked = True

            elif event.button == 3: # Right click
                del_blocks(pos)  # Delete blocks there
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                block_x2, block_y2 = pos
                create_block(block_x1, block_y1, block_x2, block_y2, color=BLOCK_COLOR, warning_color=RED_BLOCK_COLOR)
                clicked = False

    draw_blocks()  # Draw all blocks on screen
    pygame.display.update()  # Update the screen
    pygame.time.Clock().tick(60)  # Limit the game framerate to 60FPS
