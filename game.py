import pygame
import json
from math import *
from shapely.geometry import Point, box
from shapely.geometry.polygon import Polygon
from network import Network
from time import time

# Initializing Pygame
pygame.init()

# Creating the sceen
screen = pygame.display.set_mode((600, 450))

# Setting up icon and title
pygame.display.set_caption("Luigi's Mansion Game")
icon = pygame.image.load("game_icon.png")
pygame.display.set_icon(icon)

# Initialize list for walls in map and set game colors
blocks = []
BLOCK_COLOR = (89, 78, 77)  # Grey
FLASH_COLOR = (250, 232, 92)  # Yellow


def player_collision(x, y, width, height):
    # Wall collision
    if x <= 0:  # Past left border
        return True
    if x + width >= screen.get_width():  # Past right border
        return True
    if y <= 0:  # Past top border
        return True
    if y + height >= screen.get_height():  # Past bottom border
        return True

    # Block collision
    block_boxes = [block["block_box"] for block in blocks]
    player_box = box(x, y, x + width, y + height)

    for block_box in block_boxes:  # Check for each block
        if player_box.intersects(block_box):  # Check if there is a collision
            return True


def rotate(x, y, ox, oy, theta):
    """
    :param x: target point's x coordinate
    :param y: target point's y coordinate
    :param ox: origin point's x coordinate
    :param oy: origin point's y coordinate
    :param theta: counterclockwise degrees by which point should be turned
    :return: x and y coordinates of target point after rotating around origin point
    """
    theta = radians(theta)  # Convert degrees to radians
    nx = cos(theta) * (x - ox) - sin(theta) * (y - oy) + ox
    ny = sin(theta) * (x - ox) + cos(theta) * (y - oy) + oy

    return nx, ny


def flashlight(p, intensity):
    x, y, width, height, theta = p.x, p.y, p.width, p.height, p.rotation
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

        if i <= 0:
            return polygon_points

        for block_box in block_boxes:
            if tmp_flash_polygon.intersects(block_box):
                return get_flash_polygon(i - 1)

        return polygon_points

    return get_flash_polygon(intensity)


def create_block(x1, y1, x2, y2, color):
    global blocks
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1

    width = x2 - x1
    height = y2 - y1
    rect = pygame.Rect(x1, y1, width, height)
    block_box = box(x1, y1, x2, y2)

    new_block = {"x1": x1,
                 "y1": y1,
                 "x2": x2,
                 "y2": y2,
                 "color": color,
                 "rect": rect,
                 "block_box": block_box
                 }
    blocks.append(new_block)


def draw_blocks():
    for block in blocks:
        pygame.draw.rect(screen, block["color"], block["rect"])


def create_map_from_file(filename):
    with open(filename, 'r') as f:
        file_block_list = json.load(f)
        for item in file_block_list:
            create_block(item[0], item[1], item[2], item[3], item[4])
        f.close()


def get_rotation(dx, dy):
    # trigonomical funcs are computationally expensive therefore it's faster to use indexes of a small cached list
    dx = int(dx + 1)
    dy = int(dy + 1)
    rotation_list = [[135, 180, 225],
                     [90, 0, 270],
                     [45, 0, 315]]

    return rotation_list[dy][dx]


# Adding Network
n = Network()
p1 = n.getP()
p2 = n.send(p1)

# -----------------------------------------------------------------------
create_map_from_file('map.json')
# Game loop
running = True
while running:

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    p1.execEvents()

    if p1.x_vel != 0 or p1.y_vel != 0:
        p1.rotation = get_rotation(p1.x_vel / p1.speed, p1.y_vel / p1.speed)

    xlegal = not player_collision(p1.x + p1.x_vel, p1.y, p1.width, p1.height)
    ylegal = not player_collision(p1.x, p1.y + p1.y_vel, p1.width, p1.height)

    if p1.x_vel != 0 and p1.y_vel != 0 and xlegal and ylegal:
        p1.addX(p1.x_vel / 1.414)
        p1.addY(p1.y_vel / 1.414)

    else:
        if xlegal:
            p1.addX(p1.x_vel)
        if ylegal:
            p1.addY(p1.y_vel)

    draw_blocks()

    pygame.time.Clock().tick(60)

    p2 = n.send(p1)

    if p1.isHuman():
        luigi = p1
        ghost = p2
    else:
        luigi = p2
        ghost = p1

    if p2.isHuman():
        p2.show(screen)
    p1.show(screen)

    flash_polygon = Point(-1, -1)
    if luigi.flash_mode == 'on':
        flash_polygon_points = flashlight(luigi, intensity=10)
        flash_polygon = Polygon(flash_polygon_points)
        pygame.draw.polygon(screen, FLASH_COLOR,
                            flash_polygon_points)

    if ghost.box.intersects(flash_polygon):
        print(f"Ow! My health is now {ghost.health}")
        ghost.health -= 0.5
        ghost.burn()

    if ghost.burning:
        ghost.show(screen)

    if ghost.box.intersects(luigi.box) and not ghost.burning:
        luigi.lives -= 1
        print(f"Oh-a-no, i have é only {luigi.lives} lifé left")
        luigi.setCors(1, 1)

    if time() - ghost.timer > 2:
        ghost.burning = False

    p1.updateBox()
    pygame.display.update()

'''
To-DO:
- add health bar / life count
- add Game Over screen
- add start screen (waiting for player to connect)
- add sounds
- typehint funcs
'''
