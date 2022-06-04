import pygame
import json
from math import radians, cos, sin, sqrt
from shapely.geometry import Point, box
from shapely.geometry.polygon import Polygon
from typing import Tuple

from network import Network
from time import time
from player import human_spawnpoint, ghost_spawnpoint

# Initializing Pygame
pygame.init()

# Creating the borders
play_size = (800, 600)

left_border = 0
top_border = 100
right_border = left_border + play_size[0]
bottom_border = top_border + play_size[1]

# Create screen based on play size dimensions and borders
screen = pygame.display.set_mode((left_border + play_size[0], top_border + play_size[1]))

# Setting up icon and title
pygame.display.set_caption("Luigi's Mansion Game")
icon = pygame.image.load("game_icon.png")
pygame.display.set_icon(icon)

# Initialize list for walls in map and set game colors
blocks = []
BLOCK_COLOR = (89, 78, 77)  # Grey
FLASH_COLOR = (250, 232, 92)  # Yellow
HEALTH_BAR_COLOR = (219, 65, 50)  # Red
HEART_IMG = pygame.image.load("heart.png")  # 40x40 pixels


def health_bar(health: float):
    w, h, t = right_border - left_border, bottom_border - top_border, top_border  # Initialize necessary variables
    hb_left = 0.7 * w  # Calculate starting point of health bar relative to game width
    hb_size = [0.27 * w * health / 100, 0.04 * h]  # Calculate health bar dimensions based on game height and health
    # Draw centered health bar
    pygame.draw.rect(screen, HEALTH_BAR_COLOR,
                     pygame.Rect(hb_left, (t - hb_size[1]) / 2, hb_size[0], hb_size[1]))


def draw_hearts(lives: int):
    for life in range(lives):  # Draw 1 heart for every life
        # Center hearts and keep distance between them
        screen.blit(HEART_IMG, (25 + life * 45, (top_border - HEART_IMG.get_height()) / 2))


def player_collision(x: int, y: int, width: float, height: float):
    # Wall collision
    if x < left_border:  # Past left border
        return True
    if x + width > right_border:  # Past right border
        return True
    if y < top_border:  # Past top border
        return True
    if y + height > bottom_border:  # Past bottom border
        return True

    # Block collision
    block_boxes = [block["block_box"] for block in blocks]  # Create a shapely box for each box in-game
    player_box = box(x, y, x + width, y + height)

    for block_box in block_boxes:  # Check for each block
        if player_box.intersects(block_box):  # Check if there is a collision
            return True


def rotate(x: int, y: int, ox: int, oy: int, theta: int) -> Tuple[float, float]:
    """
    :param x: target point's x coordinate
    :param y: target point's y coordinate
    :param ox: origin point's x coordinate
    :param oy: origin point's y coordinate
    :param theta: counterclockwise degrees by which point should be turned
    :return: x and y coordinates of target point after rotating around origin point
    """
    theta = radians(theta)  # Convert degrees to radians
    nx = cos(theta) * (x - ox) - sin(theta) * (y - oy) + ox  # Mathematical calculation for new point's x coordinate
    ny = sin(theta) * (x - ox) + cos(theta) * (y - oy) + oy  # Mathematical calculation for new point's y coordinate

    return nx, ny  # Return new points


def flashlight(p, intensity: int):
    x, y, width, height, theta = p.x, p.y, p.width, p.height, p.rotation  # Initialize necessary variables
    intensity *= 10  # Translate intensity level into pixels

    # Create a shapely box for each box in-game
    block_boxes = [block["block_box"] for block in blocks]

    def get_flash_polygon(i):  # create multi-use function for recursion purposes
        brx, bry = x + width, y + height  # Bottom right x and y cooridnates
        blx, bly = x, y + height  # Bottom left x and y cooridnates
        ox, oy = x + width / 2, y + height / 2  # Origin point (around which points should be rotated)
        point1, point2 = rotate(brx - width / 4, bry, ox, oy, theta), \
                         rotate(blx + width / 4, bly, ox, oy, theta)  # Smaller side of the trapizoid
        point3, point4 = rotate(brx + i / 4, bry + i, ox, oy, theta), \
                         rotate(blx - i / 4, bly + i, ox, oy, theta)  # Longer side of the trapizoid

        polygon_points = [point1, point3, point4, point2]  # Add all points to list
        tmp_flash_polygon = Polygon(polygon_points)  # Create a polygon using points

        if i <= 0:  # Recursion stop condition
            return polygon_points

        for block_box in block_boxes:
            if tmp_flash_polygon.intersects(block_box):  # If the flashlight intersects one of the walls
                return get_flash_polygon(i - 1)  # Return a smaller flashlight

        return polygon_points  # Return trapizoid verticies

    return get_flash_polygon(intensity)  # Call recursion function with initial flashlight intensity


def create_block(x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int]):
    global blocks  # Make block list global so that the function will update it and not a local instance
    if x2 < x1:
        x1, x2 = x2, x1  # Update variables so x2 is always bigger than x1
    if y2 < y1:
        y1, y2 = y2, y1  # Update variables so y2 is always bigger than y1

    # Initialize necessary variables
    width = x2 - x1
    height = y2 - y1
    rect = pygame.Rect(x1, y1, width, height)
    block_box = box(x1, y1, x2, y2)

    # Create block dict out of variables
    new_block = {"x1": x1,
                 "y1": y1,
                 "x2": x2,
                 "y2": y2,
                 "color": color,
                 "rect": rect,
                 "block_box": block_box
                 }

    blocks.append(new_block)  # Append new block to total block list


def draw_blocks():
    for block in blocks:  # Loop over all the blocks
        pygame.draw.rect(screen, block["color"], block["rect"])  # Draw block


def create_map_from_file(filename: str):
    with open(filename, 'r') as f:  # Open file in reading mode
        file_block_list = json.load(f)  # Load file info with json
        for item in file_block_list:  # Loop over all blocks
            create_block(item[0], item[1], item[2], item[3], item[4])  # Create block from file info
        f.close()  # Close the file


def get_rotation(dx: float, dy: float):
    # trigonomical funcs are computationally expensive therefore it's faster to use indexes of a small cached list
    dx = int(dx + 1)  # Increment dx to match list indexing
    dy = int(dy + 1)  # Increment dy to match list indexing
    rotation_list = [[135, 180, 225],  # Create 2D list which contains possible rotation angles
                     [90, 0, 270],
                     [45, 0, 315]]

    return rotation_list[dy][dx]


# Adding Network
n = Network()  # Create network instance
p1 = n.getP()  # Get player 1 info from server
p2 = n.send(p1)  # Get player 2 info from server

# -----------------------------------------------------------------------
create_map_from_file('map.json')  # Create map blocks based on file

# Game loop
running = True
while running:

    screen.fill((0, 0, 0))  # Set screen to black
    draw_blocks()  # Draw walls

    for event in pygame.event.get():  # Loop over pygame events
        if event.type == pygame.QUIT:  # Check for quit event (click on x button)
            running = False  # Stop the while loop

    p1.execEvents()  # Check for player events (movement, flashlight, etc)

    if p1.x_vel != 0 or p1.y_vel != 0:  # If player is in motion
        p1.rotation = get_rotation(p1.x_vel / p1.speed, p1.y_vel / p1.speed)  # Update rotation

    xlegal = not player_collision(p1.x + p1.x_vel, p1.y, p1.width, p1.height)  # Check if x-axis movement is legal
    ylegal = not player_collision(p1.x, p1.y + p1.y_vel, p1.width, p1.height)  # Check if y-axis movement is legal

    if p1.x_vel != 0 and p1.y_vel != 0 and xlegal and ylegal:  # If the player is moving diagonally
        p1.addX(p1.x_vel / 1.414)  # Slow down speed in each axis taking into account the pythagorean theorem
        p1.addY(p1.y_vel / 1.414)

    else:
        if xlegal:
            p1.addX(p1.x_vel)  # Move player in the x-axis
        if ylegal:
            p1.addY(p1.y_vel)  # Move player in the y-axis

    p2 = n.send(p1)  # Send player 1's info to server and update player 2 on screen based on server response

    #  Check which player is the human and which one is the ghost
    if p1.isHuman():
        luigi = p1
        ghost = p2
    else:
        luigi = p2
        ghost = p1

    if p2.isHuman():
        p2.show(screen)  # Show opponent only if it is the human
    p1.show(screen)

    flash_polygon = Point(-1, -1)  # Initialize arbitrary point for the flashlight polygon
    if luigi.flash_mode == 'on':  # Check if flashlight is on
        flash_polygon_points = flashlight(luigi, intensity=10)  # Get flashlight trapizoid verticies
        flash_polygon = Polygon(flash_polygon_points)  # Create trapizoid out of verticies
        pygame.draw.polygon(screen, FLASH_COLOR, flash_polygon_points)  # Draw flashlight based on trapizoid

    if ghost.box.intersects(flash_polygon):  # If the flashlight hit the ghost
        print(f"Ow! My health is now {ghost.health}")
        ghost.health -= 0.5  # Lower ghost's health
        ghost.burn()  # Update ghost object to be burning

    if ghost.box.intersects(luigi.box) and not ghost.visible:  # If the ghost is invisible and is touching the human
        luigi.lives -= 1  # Lower one of the human's lives
        print(f"Oh-a-no, i have é only {luigi.lives} livés é left")
        luigi.setCors(human_spawnpoint[0], human_spawnpoint[1])  # Return human to spawnpoint

    # If the ghost is burning and the distance between the human and the ghost is smaller than 120 pixels
    if ghost.burning and sqrt(((luigi.x + luigi.width / 2) - (ghost.x + ghost.width / 2)) ** 2 +
                              ((luigi.y + luigi.height / 2) - (ghost.y + ghost.height / 2)) ** 2) < 120:
        ghost.timer = time()  # Reset the ghost timer (so that he stays visible on screen)

    if time() - ghost.timer > 2 and ghost.burning:  # If the ghost has been burning for longer than 2 seconds
        ghost.burning = False  # Stop burning
        ghost.speed = 5  # Revert to normal speed

    if ghost.visible:
        ghost.show(screen)  # Show the ghost on screen if it's burning or dashing

    health_bar(ghost.health)  # Display ghost health bar
    draw_hearts(luigi.lives)  # Display human lives
    p1.updateBox()  # Update player hitbox
    pygame.display.update()  # Update screen
    pygame.time.Clock().tick(60)  # Tick the game a constant amount (60fps)

'''
To-DO:
- add Game Over screen
- add start screen (waiting for player to connect)
- add sounds
- make better flashlight
- add ghost dash ability
- add indicator if ghost is visible (on ghost's screen)
- ghost should be faster when burnt
'''
