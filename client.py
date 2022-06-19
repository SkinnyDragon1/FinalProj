import pygame
import json
from math import radians, cos, sin, copysign
from shapely.geometry import Point, box
from shapely.geometry.polygon import Polygon
from typing import Tuple, cast, List

from block import Block
from network import Network
from time import time
from player import human_spawnpoint, ghost_spawnpoint, Player, Human, Ghost
from astar import create_grid_from_file, findpath
from button import Button
from random import choice

# Initializing Pygame
pygame.init()
pygame.font.init()

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
icon = pygame.image.load("images/game_icon.png")
pygame.display.set_icon(icon)

# Initialize list for walls in map
blocks = []
# Initialize game colors
BLOCK_COLOR = (89, 78, 77)  # Grey
FLASH_COLOR = (250, 232, 92)  # Yellow
HEALTH_BAR_COLOR = (219, 65, 50)  # Red
# Load game images
HEART_IMG = pygame.image.load("images/heart.png")  # 40x40 pixels
FIRE_IMG = pygame.image.load("images/fire.png")  # 64x64 pixels
EYE_IMG = pygame.image.load("images/eye.png")  # 64x64 pixels
luigibg = pygame.image.load("images/luigibg.png")
ghostbg = pygame.image.load("images/ghostbg1.png")
# Load game sounds
caught_by_ghost = pygame.mixer.Sound("sounds/Caught By Ghost.mp3")
ghost_wins = pygame.mixer.Sound("sounds/Ghost Wins.mp3")
ghost_loses = pygame.mixer.Sound("sounds/Ghost Loses.mp3")
ghost_8 = pygame.mixer.Sound("sounds/Ghost 8.mp3")  # length = 0.75s
# Determine framerate
FRAMERATE = 60


def waiting_room() -> None:
    screen.fill((0, 0, 0))  # Set screen to black

    font = pygame.font.SysFont("comicsans",
                               int(screen.get_width() / 12))  # Set font and size (relative to screen width)
    text = font.render("Waiting for player...", True, (255, 255, 255))  # Create text
    screen.blit(text, (100, 300))  # Put text on screen

    pygame.display.update()

    for event in pygame.event.get():  # Loop over pygame events
        if event.type == pygame.QUIT:  # Check for quit event (click on x button)
            exit()  # Quit the game


def health_bar(health: float) -> None:
    w, h, t = right_border - left_border, bottom_border - top_border, top_border  # Initialize necessary variables
    hb_left = 0.7 * w  # Calculate starting point of health bar relative to game width
    hb_size = [0.27 * w * health / 100, 0.04 * h]  # Calculate health bar dimensions based on game height and health
    # Draw centered health bar
    pygame.draw.rect(screen, HEALTH_BAR_COLOR,
                     pygame.Rect(hb_left, (t - hb_size[1]) / 2, hb_size[0], hb_size[1]))


def draw_hearts(lives: int) -> None:
    for life in range(lives):  # Draw 1 heart for every life
        # Center hearts and keep distance between them
        screen.blit(HEART_IMG, (25 + life * 45, (top_border - HEART_IMG.get_height()) / 2))


def show_icons(p) -> None:
    w = right_border - left_border
    if p.isGhost():  # Show only if current player is the ghost
        if p.burning:
            screen.blit(FIRE_IMG, (w / 2 - 36 - FIRE_IMG.get_width(),
                                   (top_border - FIRE_IMG.get_height()) / 2))  # Draw fire icon relative to screen size
        if p.visible:
            screen.blit(EYE_IMG,
                        (w / 2, (top_border - EYE_IMG.get_height()) / 2))  # Draw eye icon relative to screen size


def player_collision(x: int, y: int, width: float, height: float) -> bool:
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
    block_boxes = [block.block_box for block in blocks]  # Create a shapely box for each box in-game
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


def flashlight(p, intensity: int) -> List[Tuple[float, float]]:
    x, y, width, height, theta = p.x, p.y, p.width, p.height, p.rotation  # Initialize necessary variables
    intensity *= 10  # Translate intensity level into pixels

    # Create a shapely box for each box in-game
    block_boxes = [block.block_box for block in blocks]

    def get_flash_polygon(i):  # create multi-use function for recursion purposes
        brx, bry = x + width, y + height  # Bottom right x and y cooridnates
        blx, bly = x, y + height  # Bottom left x and y cooridnates
        ox, oy = x + width / 2, y + height / 2  # Origin point (around which points should be rotated)
        point1, point2 = rotate(brx - width / 4, bry, ox, oy, theta), \
                         rotate(blx + width / 4, bly, ox, oy, theta)  # Smaller side of the trapizoid
        point3, point4 = rotate(brx + i / 8, bry + i, ox, oy, theta), \
                         rotate(blx - i / 8, bly + i, ox, oy, theta)  # Longer side of the trapizoid

        polygon_points = [point1, point3, point4, point2]  # Add all points to list
        tmp_flash_polygon = Polygon(polygon_points)  # Create a polygon using points

        if i <= 0:  # Recursion stop condition
            return polygon_points

        for block_box in block_boxes:
            if tmp_flash_polygon.intersects(block_box):  # If the flashlight intersects one of the walls
                return get_flash_polygon(i - 1)  # Return a smaller flashlight

        return polygon_points  # Return trapizoid verticies

    return get_flash_polygon(intensity)  # Call recursion function with initial flashlight intensity


def create_block(x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int]) -> None:
    global blocks  # Make block list global so that the function will update it and not a local instance

    new_block = Block(x1, y1, x2, y2, color)

    blocks.append(new_block)  # Append new block to total block list


def draw_blocks() -> None:
    for block in blocks:  # Loop over all the blocks
        block.draw(screen)  # Draw block


def create_map_from_file(filename: str, tp: int) -> None:
    with open(filename, 'r') as f:  # Open file in reading mode
        file_block_list = json.load(f)  # Load file info with json
        for item in file_block_list:  # Loop over all blocks
            create_block(item[0], item[1] + tp, item[2], item[3] + tp, item[4])  # Create block from file info
        f.close()  # Close the file


def get_rotation(xvel: int, yvel: int) -> int:
    dx = copysign(1, xvel) if xvel != 0 else 0  # Turn xvel into speed direction instead of value
    dy = copysign(1, yvel) if yvel != 0 else 0  # Turn yvel into speed direction instead of value
    """
    dx: direction of x-velocity; either +1, -1, or 0 depending on the direction of the player in the x-axis
    dy: direction of y-velocity; either +1, -1, or 0 depending on the direction of the player in the y-axis
    :return: the angle in which the player is looking, in increments of 45
    """
    dx = int(dx + 1)  # Increment dx to match list indexing
    dy = int(dy + 1)  # Increment dy to match list indexing
    # trigonomical funcs are computationally expensive therefore it's faster to use indexes of a small cached list
    rotation_list = [[135, 180, 225],  # Create 2D list which contains possible rotation angles
                     [90, 0, 270],
                     [45, 0, 315]]

    return rotation_list[dy][dx]


def check_for_end(player1: Player, h: Human, g: Ghost) -> bool:
    if h.lives <= 0:  # If human has lost
        winner = g  # Set winner to ghost
        return game_over(player1, winner)  # Call game over function with ghost as winner
    if g.health <= 0:  # If ghost has lost
        winner = h  # Set winner to human
        return game_over(player1, winner)  # Call game over function with human as winner

    return True


def game_over(player1: Player, winner: Player) -> bool:
    if player1 == winner:  # If current player is the winner
        result_text = "You Won!"  # Set matching text
        clr = (0, 255, 0)  # Set matching color (green)
    else:  # If current player is the loser
        result_text = "You Lost!"  # Set matching text
        clr = (255, 0, 0)  # Set matching color (red)

    font = pygame.font.SysFont("comicsans",
                               int(screen.get_width() / 10))  # Set font and size (relative to screen width)
    text = font.render(result_text, True, clr)  # Create text
    screen.blit(text, (200, 300))  # Put text on screen

    end_sound = ghost_wins if winner.isGhost() else ghost_loses  # Set matching end sound
    pygame.mixer.music.stop()  # Stop the music that is currently playing
    pygame.mixer.stop()  # Stop all sound effects
    pygame.mixer.Sound.play(end_sound)  # Play end game sound

    pygame.display.update()  # Update the screen

    for _ in range(60 * 20):  # Play for 20 seconds

        for event in pygame.event.get():  # Loop over pygame events
            if event.type == pygame.QUIT:  # Check for quit event (click on x button)
                quit()

        pygame.time.Clock().tick(60)

    pygame.mixer.music.stop()  # Stop the music that is currently playing
    pygame.mixer.stop()  # Stop all sound effects
    pygame.mixer.music.unload()  # Unload music track

    screen.fill((0, 0, 0))  # Set screen to black
    pygame.display.update()  # Update the screen

    return False  # Return false (the game should stop running)


def MultiplayerGame():
    # Setting up connection to server
    n = Network()  # Create network instance
    p1, game = n.getWaitingState()  # Get player 1 info from server

    while not game.connected():
        p1, game = n.getWaitingState()
        waiting_room()

    # -----------------------------------------------------------------------
    create_map_from_file('map.json', top_border)  # Create map blocks based on file

    pygame.mixer.music.stop()  # Stop previous music
    pygame.mixer.music.unload()  # Unload previous track
    pygame.mixer.music.load("sounds/Background Music.mp3")  # Load new music
    pygame.mixer.music.play(-1)  # Play music on repeat

    last_played = time() - 0.75  # Keep track of last time effect was played so that sounds don't overlap

    # Game loop
    running = True
    while running:  # Game should keep looping until game over

        screen.fill((0, 0, 0))  # Set screen to black
        draw_blocks()  # Draw walls

        for e in pygame.event.get():  # Loop over pygame events
            if e.type == pygame.QUIT:  # Check for quit event (click on x button)
                quit()

        p1.execEvents()  # Check for player events (movement, flashlight, etc)

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
            human: Human = cast(Human, p1)
            ghost: Ghost = cast(Ghost, p2)
        else:
            human: Human = cast(Human, p2)
            ghost: Ghost = cast(Ghost, p1)

        if human.x_vel != 0 or human.y_vel != 0:
            human.rotation = get_rotation(human.x_vel, human.y_vel)

        if p2.isHuman():
            p2.show(screen)  # Show opponent only if it is the human
        p1.show(screen)

        flash_polygon = Point(-1, -1)  # Initialize arbitrary point for the flashlight polygon
        if human.flash_mode == 'on':  # Check if flashlight is on
            flash_polygon_points = flashlight(human, intensity=7)  # Get flashlight trapizoid verticies
            flash_polygon = Polygon(flash_polygon_points)  # Create trapizoid out of verticies
            pygame.draw.polygon(screen, FLASH_COLOR, flash_polygon_points)  # Draw flashlight based on trapizoid

        if ghost.box.intersects(flash_polygon):  # If the flashlight hit the ghost
            ghost.health -= 0.5  # Lower ghost's health
            ghost.burn()  # Update ghost object to be burning
            print(f"Ow! My health is now {ghost.health}")
            if time() - last_played > 0.8:  # Check if enough time has passed since last time sound effect was played
                last_played = time()  # Update last time played
                pygame.mixer.Sound.play(ghost_8)

        if ghost.box.intersects(human.box) and not ghost.visible:  # If the ghost is invisible and is touching the human
            if time() - human.timer > 3:  # Check for human invincibility
                human.lives -= 1  # Lower one of the human's lives
                pygame.mixer.Sound.play(caught_by_ghost)  # Play sound effect
                print(f"Oh-a-no, i have é only {human.lives} livés é left")
                human.setCors(human_spawnpoint[0], human_spawnpoint[1])  # Return human to spawnpoint
                human.timer = time()

        # If the ghost is burning and the distance between the human and the ghost is smaller than 120 pixels
        if ghost.burning and ghost.distance(human) < 120:
            ghost.timer = time()  # Reset the ghost timer (so that he stays visible on screen)

        if time() - ghost.timer > 2 and ghost.burning:  # If the ghost has been burning for longer than 2 seconds
            ghost.burning = False  # Stop burning
            ghost.speed = 3  # Revert to normal speed

        if ghost.visible:
            ghost.show(screen)  # Show the ghost on screen if it's burning or dashing

        health_bar(ghost.health)  # Display ghost health bar
        draw_hearts(human.lives)  # Display human lives
        p1.updateBox()  # Update player hitbox
        show_icons(p1)  # Draw necessary icons (only if p1 is the ghost)
        running = check_for_end(p1, human, ghost)  # Check if game has ended and if so stop the while loop
        pygame.display.update()  # Update screen
        pygame.time.Clock().tick(60)  # Tick the game a constant amount (60fps)


def SingleplayerGame():
    create_map_from_file('map.json', top_border)  # Create map blocks based on file
    grid_1 = create_grid_from_file('map.json', 800, 15, 20)  # Create a grid for pathfinding based on file
    grid_2 = create_grid_from_file('map.json', 800, 30, 40)  # Create a more detailed grid for specific cases
    ticknum = 0  # Keep track of the number of ticks
    pygame.mixer.music.stop()  # Stop previous music
    pygame.mixer.music.unload()  # Unload previous track
    pygame.mixer.music.load("sounds/Background Music.mp3")  # Load music track
    pygame.mixer.music.play(-1)  # Play music on repeat

    last_played = time() - 0.75  # Keep track of last time effect was played so that sounds don't overlap

    p1: Human = Human(human_spawnpoint[0], human_spawnpoint[1])
    p2: Ghost = Ghost(ghost_spawnpoint[0], ghost_spawnpoint[1])
    path = findpath(grid_1, (p2.x, p2.y - top_border), (p1.x, p1.y - top_border))  # Create first path
    should_dash = False
    lr, tb = choice([right_border, left_border]), choice([bottom_border, top_border]) - top_border
    # Game loop
    running = True
    while running:  # Game should keep looping until game over

        screen.fill((0, 0, 0))  # Set screen to black
        draw_blocks()  # Draw walls

        for e in pygame.event.get():  # Loop over pygame events
            if e.type == pygame.QUIT:  # Check for quit event (click on x button)
                quit()

        p1.execEvents()  # Check for player events (movement, flashlight, etc)

        '''UPDATE PLAYER-2 HERE'''
        # Update the path a constant amount of times per second (Not every tick so that game doesn't lag)
        if ticknum % (FRAMERATE / 12) == 0:  # 5 times a second
            ghost_cors = (p2.x + p2.width / 2, p2.y - top_border + p2.height / 2)
            if p2.burning:
                if ticknum % (FRAMERATE / 0.2) == 0:  # Once every 5 seconds
                    lr, tb = choice([right_border, left_border]), choice([bottom_border, top_border]) - top_border
                path = findpath(grid_1, ghost_cors, (lr, tb))

            else:
                path = findpath(grid_1, ghost_cors, (p1.x, p1.y - top_border))
                should_dash = False  # Set default assumption (ghost shouldn't be dashing)

                if len(path) >= 15:
                    should_dash = True  # If the ghost is far from the player, he should dash

                elif len(path) == 0:  # If no path was found, try using the more detailed grid
                    path = findpath(grid_2, (p2.x + p2.width / 2, p2.y - top_border + p2.height / 2),
                                    (p1.x, p1.y - top_border))

                    if len(path) >= 30:
                        should_dash = True  # If the ghost is far from the player, he should dash

        p2.followPath(path, top_border)  # Follow current path
        p2.dash(should_dash)

        if p1.x_vel != 0 or p1.y_vel != 0:
            p1.rotation = get_rotation(p1.x_vel, p1.y_vel)

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

        xlegal = not player_collision(p2.x + p2.x_vel, p2.y, p2.width, p2.height)  # Check if x-axis movement is legal
        ylegal = not player_collision(p2.x, p2.y + p2.y_vel, p2.width, p2.height)  # Check if y-axis movement is legal

        if p2.x_vel != 0 and p2.y_vel != 0 and xlegal and ylegal:  # If the player is moving diagonally
            p2.addX(p2.x_vel / 1.414)  # Slow down speed in each axis taking into account the pythagorean theorem
            p2.addY(p2.y_vel / 1.414)

        else:
            if xlegal:
                p2.addX(p2.x_vel)  # Move player in the x-axis
            if ylegal:
                p2.addY(p2.y_vel)  # Move player in the y-axis

        # Don't show ghost to human
        # p2.show(screen)
        p1.show(screen)

        flash_polygon = Point(-1, -1)  # Initialize arbitrary point for the flashlight polygon
        if p1.flash_mode == 'on':  # Check if flashlight is on
            flash_polygon_points = flashlight(p1, intensity=7)  # Get flashlight trapizoid verticies
            flash_polygon = Polygon(flash_polygon_points)  # Create trapizoid out of verticies
            pygame.draw.polygon(screen, FLASH_COLOR, flash_polygon_points)  # Draw flashlight based on trapizoid

        if p2.box.intersects(flash_polygon):  # If the flashlight hit the ghost
            p2.health -= 0.5  # Lower ghost's health
            p2.burn()  # Update ghost object to be burning
            print(f"Ow! My health is now {p2.health}")
            if time() - last_played > 0.8:  # Check if enough time has passed since last time sound effect was played
                last_played = time()  # Update last time played
                pygame.mixer.Sound.play(ghost_8)

        if p2.box.intersects(p1.box) and not p2.visible:  # If the ghost is invisible and is touching the human
            if time() - p1.timer > 3:  # Check for human invincibility
                p1.lives -= 1  # Lower one of the human's lives
                pygame.mixer.Sound.play(caught_by_ghost)  # Play sound effect
                print(f"Oh-a-no, i have é only {p1.lives} livés é left")
                p1.setCors(human_spawnpoint[0], human_spawnpoint[1])  # Return human to spawnpoint
                p1.timer = time()

        # If the ghost is burning and the distance between the human and the ghost is smaller than 120 pixels
        if p2.burning and p2.distance(p1) < 120:
            p2.timer = time()  # Reset the ghost timer (so that he stays visible on screen)

        if time() - p2.timer > 2 and p2.burning:  # If the ghost has been burning for longer than 2 seconds
            p2.burning = False  # Stop burning
            p2.speed = 3  # Revert to normal speed

        if p2.visible:
            p2.show(screen)  # Show the ghost on screen if it's burning or dashing

        health_bar(p2.health)  # Display ghost health bar
        draw_hearts(p1.lives)  # Display human lives
        p1.updateBox()  # Update player 1's hitbox
        p2.updateBox()  # Update player 2's hitbox
        running = check_for_end(p1, p1, p2)  # Check if game has ended and if so stop the while loop
        pygame.display.update()  # Update screen
        pygame.time.Clock().tick(FRAMERATE)  # Tick the game a constant amount (60fps)
        ticknum += 1  # Increment the tick count


def how_to_play_screen():
    back_button = Button("Back", 10, 10, 80, 40, (181, 44, 34), (201, 59, 48), 30, main)

    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        screen.fill((0, 0, 0))  # Set screen to black

        font_1 = pygame.font.SysFont("comicsans", 90)
        htp_text = font_1.render("How To Play:", True, (232, 201, 44))

        font_2 = pygame.font.SysFont("comicsans", 60)
        human_text = font_2.render("Human", True, (25, 135, 8))
        ghost_text = font_2.render("Ghost", True, (233, 240, 197))

        font_3 = pygame.font.SysFont("comicsans", 30)
        human_explain_text = "Your job is to find$and burn the ghost$using your flashlight.$$WASD to move.$$Space to flash light."
        human_explain_text = human_explain_text.split("$")
        for num, line in enumerate(human_explain_text):
            explain_txt = font_3.render(line, True, (25, 135, 8))
            text_rect = explain_txt.get_rect(center=(163, 390 + 32 * num))
            screen.blit(explain_txt, text_rect)

        ghost_explain_text = "Your job is to$capture the human$without beeing seen.$$WASD to move.$$Space to dash."
        ghost_explain_text = ghost_explain_text.split("$")
        for num, line in enumerate(ghost_explain_text):
            explain_txt = font_3.render(line, True, (233, 240, 197))
            text_rect = explain_txt.get_rect(center=(632, 390 + 32 * num))
            screen.blit(explain_txt, text_rect)

        pos = pygame.mouse.get_pos()
        back_button.draw(screen, pos)

        screen.blit(htp_text, (150, 80))
        screen.blit(human_text, (70, 250))
        screen.blit(ghost_text, (550, 250))
        # screen.blit(human_explain_text, (20, 200))
        # screen.blit(ghost_explain_text, (350, 200))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()  # Track mouse coordinates
                back_button.click(pos)


def main():
    screen.fill((0, 0, 0))  # Set screen to black
    pygame.mixer.music.load("sounds/Opening.mp3")  # Load music track
    pygame.mixer.music.play(-1)  # Play music on repeat

    btns = [Button("How to Play", 250, 300, 300, 150, (89, 78, 77), (133, 117, 115), 50, how_to_play_screen),
            Button("Singleplayer", 250, 460, 145, 72.5, (89, 78, 77), (133, 117, 115), 20, SingleplayerGame),
            Button("Multiplayer", 405, 460, 145, 72.5, (89, 78, 77), (133, 117, 115), 20, MultiplayerGame)]

    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)

        screen.blit(ghostbg, (5, 350))
        screen.blit(luigibg, (620, 300))

        font = pygame.font.SysFont("comicsans", 90)
        text1 = font.render("Luigi's Ghost", True, (232, 201, 44))
        text2 = font.render("Mansion", True, (232, 201, 44))
        screen.blit(text1, (150, 50))
        screen.blit(text2, (230, 150))

        pos = pygame.mouse.get_pos()
        for btn in btns:
            btn.draw(screen, pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()  # Track mouse coordinates
                for btn in btns:
                    btn.click(pos)

        pygame.display.update()


while True:
    main()
