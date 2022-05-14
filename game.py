import pygame
import json
from math import *
from shapely.geometry import Point, box
from shapely.geometry.polygon import Polygon
from player import Player, Human, Ghost
from network import Network
from time import perf_counter

# Initializing Pygame
pygame.init()

# Creating the sceen
screen = pygame.display.set_mode((600, 450))

# Setting up icon and title
pygame.display.set_caption("Luigi's Mansion Game")
icon = pygame.image.load("game_icon.png")
pygame.display.set_icon(icon)

# luigi = Human('blank.png', -1, -1)
# ghost = Ghost('blank.png', -1, -1)
# p1 = Human('blank.png', -1, -1)
# p2 = Player('blank.png', -1, -1)

blocks = []
BLOCK_COLOR = (89, 78, 77)  # Grey
FLASH_COLOR = (250, 232, 92)  # Yellow


def player_block_collision(x, y, width, height):
    # Wall collision
    if x <= 0:
        return True
    if x + width >= screen.get_width():
        return True
    if y <= 0:
        return True
    if y + height >= screen.get_height():
        return True

    # Block collision
    block_rects = [block[5] for block in blocks]  # Block : [x1, y1, x2, y2, color, Rect] --> block[5] = Rect
    player_rect = pygame.Rect(x, y, width, height)
    for block_rect in block_rects:  # Check for each block
        if player_rect.colliderect(block_rect):  # Check if there is a collision
            return True


def point_block_collision(x, y):
    block_rects = [block[5] for block in blocks]  # Block : [x1, y1, x2, y2, color, Rect] --> block[5] = Rect
    for block_rect in block_rects:
        if block_rect.collidepoint((x, y)):  # Check if there is a collision
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


def flashlight(x, y, width, height, intensity, theta):
    intensity *= 10  # Translate intensity level into pixels

    # Create a shapely box for each box in-game
    block_rects = [box(block[0], block[1], block[2], block[3]) for block in blocks]

    def get_flash_polygon(i):  # create multi-use function for recursion purposes
        brx, bry = x + width, y + height  # Bottom right x and y cooridnates
        blx, bly = x, y + height  # Bottom left x and y cooridnates
        ox, oy = x + width / 2, y + height / 2  # Origin point (around which points should be rotated)
        p1, p2 = rotate(brx - width / 4, bry, ox, oy, theta), \
                 rotate(blx + width / 4, bly, ox, oy, theta)  # Smaller side of the trapizoid
        p3, p4 = rotate(brx + i / 4, bry + i, ox, oy, theta), \
                 rotate(blx - i / 4, bly + i, ox, oy, theta)  # Longer side of the trapizoid

        polygon_points = [p1, p3, p4, p2]  # Add all points to list
        tmp_flash_polygon = Polygon(polygon_points)  # Create a polygon using points

        for block_rect in block_rects:
            if tmp_flash_polygon.intersects(block_rect):
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
    new_block = [x1, y1, x2, y2, color, rect]
    blocks.append(new_block)


def draw_blocks():
    for block in blocks:
        pygame.draw.rect(screen, block[4], block[5])


def create_map_from_file(filename):
    with open(filename, 'r') as f:
        file_block_list = json.load(f)
        for item in file_block_list:
            create_block(item[0], item[1], item[2], item[3], item[4])
        f.close()


def get_rotation(dx, dy):
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
if p1.isHuman():
    luigi = p1
    ghost = p2
else:
    luigi = p2
    ghost = p1

# -----------------------------------------------------------------------
create_map_from_file('map.json')

# Game loop
running = True
while running:

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keybind check
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                p1.x_vel = -p1.speed

            if event.key == pygame.K_d:
                p1.x_vel = p1.speed

            if event.key == pygame.K_w:
                p1.y_vel = -p1.speed

            if event.key == pygame.K_s:
                p1.y_vel = p1.speed

            if event.key == pygame.K_p:
                print(ghost.burning, ghost.timer)

            if event.key == pygame.K_SPACE and p1.isHuman():
                p1.flash_mode = 'on'

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a and luigi.x_vel != luigi.speed:
                p1.x_vel = 0
            if event.key == pygame.K_d and p1.x_vel != -p1.speed:
                p1.x_vel = 0
            if event.key == pygame.K_w and p1.y_vel != p1.speed:
                p1.y_vel = 0
            if event.key == pygame.K_s and p1.y_vel != -p1.speed:
                p1.y_vel = 0
            if event.key == pygame.K_SPACE and p1.isHuman():
                p1.flash_mode = 'off'

    if p1.x_vel != 0 or p1.y_vel != 0:
        p1.rotation = get_rotation(p1.x_vel / p1.speed, p1.y_vel / p1.speed)

    if not player_block_collision(p1.x + p1.x_vel, p1.y, p1.width, p1.height):
        p1.addX(p1.x_vel)
    if not player_block_collision(p1.x, p1.y + p1.y_vel, p1.width, p1.height):
        p1.addY(p1.y_vel)

    draw_blocks()
    # pygame.draw.circle(screen, (255, 0, 0), (400, 300), 4)
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
        flash_polygon_points = flashlight(luigi.x, luigi.y, luigi.width, luigi.height, intensity=10, theta=luigi.rotation)
        flash_polygon = Polygon(flash_polygon_points)
        pygame.draw.polygon(screen, FLASH_COLOR,
                            flash_polygon_points)

    if box(ghost.x, ghost.y, ghost.x + ghost.width, ghost.y + ghost.height).intersects(flash_polygon):
        # print(f"Ow! My health is now {ghost.health}")
        ghost.health -= 0.4
        ghost.burn()

    if ghost.burning:  # Is burning neccessary? Sperate 2 files? Which counter is it using?
        ghost.show(screen)

    if perf_counter() - ghost.timer > 2 and perf_counter() > 3:
        ghost.burning = False

    pygame.display.update()
