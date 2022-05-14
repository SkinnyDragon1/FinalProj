import pygame
import json
from os import getcwd
from math import *
from shapely.geometry import Point, box
from shapely.geometry.polygon import Polygon
from player import Player, Human, Ghost
from network import Network

# Initializing Pygame
pygame.init()

# Creating the sceen
screen = pygame.display.set_mode((600, 450))

# Setting up icon and title
pygame.display.set_caption("Luigi's Mansion - Luigi")
icon = pygame.image.load("game_icon.png")
pygame.display.set_icon(icon)

# luigi = Human('blank.png', -1, -1)
# ghost = Ghost('blank.png', -1, -1)
# p1 = Human('blank.png', -1, -1)
# p2 = Player('blank.png', -1, -1)

blocks = []
BLOCK_COLOR = (89, 78, 77)
FLASH_COLOR = (250, 232, 92)


def human_block_collision(x, y, width, height):
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
    block_rects = [block[5] for block in blocks]
    player_rect = pygame.Rect(x, y, width, height)
    for block_rect in block_rects:
        if player_rect.colliderect(block_rect):
            return True


def point_block_collision(x, y):
    block_rects = [block[5] for block in blocks]
    for block_rect in block_rects:
        if block_rect.collidepoint((x, y)):
            return True


def rotate(x, y, ox, oy, theta):
    # ox, oy = player_x + player_width / 2, player_y + player_height / 2
    theta = radians(theta)
    nx = cos(theta) * (x - ox) - sin(theta) * (y - oy) + ox
    ny = sin(theta) * (x - ox) + cos(theta) * (y - oy) + oy

    return nx, ny


def flashlight(x, y, width, height, intensity, theta):
    intensity *= 10

    def get_flash_polygon(i):
        brx, bry = x + width, y + height
        blx, bly = x, y + height
        ox, oy = x + width / 2, y + height / 2
        p1, p2 = rotate(brx - width / 4, bry, ox, oy, theta), rotate(blx + width / 4, bly, ox, oy, theta)
        p3, p4 = rotate(brx + i / 4, bry + i, ox, oy, theta), rotate(blx - i / 4, bly + i, ox, oy, theta)

        polygon_points = [p1, p3, p4, p2]

        return polygon_points

    block_rects = [box(block[0], block[1], block[2], block[3]) for block in blocks]
    collide = False
    flash_polygon = Polygon(get_flash_polygon(intensity))

    for block_rect in block_rects:
        if flash_polygon.intersects(block_rect):
            collide = True

    while collide and intensity > 0:
        intensity -= 1
        flash_polygon = Polygon(get_flash_polygon(intensity))
        collide = False
        for block_rect in block_rects:
            if flash_polygon.intersects(block_rect):
                collide = True

    pygame.draw.polygon(screen, FLASH_COLOR,
                        get_flash_polygon(intensity))


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

    if not human_block_collision(p1.x + p1.x_vel, p1.y, p1.width, p1.height):
        p1.addX(p1.x_vel)
    if not human_block_collision(p1.x, p1.y + p1.y_vel, p1.width, p1.height):
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

    p2.show(screen)
    p1.show(screen)
    if luigi.flash_mode == 'on':
        flashlight(luigi.x, luigi.y, luigi.width, luigi.height, intensity=10, theta=luigi.rotation)
        print("drawing light")
    pygame.display.update()
