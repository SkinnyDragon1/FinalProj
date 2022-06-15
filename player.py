from math import sqrt, copysign
import pygame
from time import time
from shapely.geometry import box
from typing import Dict, List, Tuple

pygame.init()
ghost_dash = pygame.mixer.Sound("sounds/Ghost Dash.wav")


class Player:
    def __init__(self, img, stx, sty):
        self.img = img
        self.width = pygame.image.load(self.img).get_width()
        self.height = pygame.image.load(self.img).get_height()
        self.x = stx
        self.y = sty
        self.box = box(self.x, self.y, self.x + self.width, self.y + self.height)
        self.x_vel = 0
        self.y_vel = 0
        self.speed = 3

        self._actionkeys: Dict[str, any] = {
            # Dictionary which translates key values to lambda functions
            "movement": {
                "xaxis": {pygame.K_a: lambda speed: self.setXvel(-speed),
                          pygame.K_d: lambda speed: self.setXvel(speed)},

                "yaxis": {pygame.K_w: lambda speed: self.setYvel(-speed),
                          pygame.K_s: lambda speed: self.setYvel(speed)}
            }
        }

    def execEvents(self):
        keys = pygame.key.get_pressed()  # Get all pressed keys

        for axis in self._actionkeys["movement"]:
            for key in self._actionkeys["movement"][axis]:
                if keys[key]:  # If key is pressed
                    self._actionkeys["movement"][axis][key](self.speed)  # Update velocity in axis
                    break  # Stop checking in this axis
                else:
                    self._actionkeys["movement"][axis][key](0)  # Set velocity to 0

    def show(self, screen):
        screen.blit(pygame.image.load(self.img), (self.x, self.y))

    def addX(self, a):
        self.x += a

    def addY(self, a):
        self.y += a

    def setXvel(self, xv):
        self.x_vel = xv

    def setYvel(self, yv):
        self.y_vel = yv

    def setCors(self, x, y):
        self.x = x
        self.y = y

    def distance(self, p):
        # Returns Euclidean distance from another player
        return sqrt(((self.x + self.width / 2) - (p.x + p.width / 2)) ** 2 +
                    ((self.y + self.height / 2) - (p.y + p.height / 2)) ** 2)

    def updateBox(self):
        self.box = box(self.x, self.y, self.x + self.width, self.y + self.height)

    def isHuman(self):
        return type(self).__name__ == 'Human'

    def isGhost(self):
        return not self.isHuman()


class Human(Player):
    def __init__(self, stx, sty):
        super().__init__("images/human.png", stx, sty)  # Inherits from player class
        self.flash_mode = "off"
        self.lives = 3
        self.rotation = 0

        _playerkeys = {
            "flashlight": {pygame.K_SPACE: lambda state: self.flashlight(state)}
        }
        self._actionkeys.update(_playerkeys)

    def flashlight(self, state):
        # Update flash_mode relative to state
        if state:
            self.flash_mode = "on"
        else:
            self.flash_mode = "off"

    def execEvents(self):
        # Update function to include space bar keystroke
        super().execEvents()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            self._actionkeys["flashlight"][pygame.K_SPACE](True)
        else:
            self._actionkeys["flashlight"][pygame.K_SPACE](False)


class Ghost(Player):

    def __init__(self, stx, sty):
        super().__init__("images/ghost.png", stx, sty)  # Inherits from player class
        self.health = 100
        self.timer = time()
        self.burning = False
        self.visible = False
        self.dashing = False

        _playerkeys = {
            "dash": {pygame.K_SPACE: lambda d: self.dash(d)}
        }
        self._actionkeys.update(_playerkeys)

    def burn(self):
        self.timer = time()  # Update time since last burn
        self.burning = True
        self.visible = True
        self.speed = 4  # Increase speed

    def dash(self, d):
        if d:
            if not self.dashing:  # If not already dashing
                self.speed = 5  # Update speed
                self.dashing = True
                self.visible = True
                pygame.mixer.Sound.play(ghost_dash)  # Play sound effect
        else:
            self.dashing = False
            if not self.burning:
                self.visible = False
                self.speed = 3

    def execEvents(self):
        super().execEvents()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            self._actionkeys["dash"][pygame.K_SPACE](True)
        else:
            self._actionkeys["dash"][pygame.K_SPACE](False)

    def followPath(self, path: List[Tuple[int, int]], top_border):
        if len(path) == 0:
            self.setXvel(0)  # Stop the ghost from moving
            self.setYvel(0)
            return  # Stop the function

        print(path[0])

        spot1_x = path[0][0]
        spot1_y = path[0][1] + top_border
        dx = spot1_x - self.x  # Difference in distance
        dy = spot1_y - self.y  # Difference in distance

        x_vel = copysign(self.speed, dx) if dx != 0 else 0
        y_vel = copysign(self.speed, dy) if dy != 0 else 0

        print(f'XVEL: {x_vel}    YVEL: {y_vel}')
        print(f"X: {self.x}      Y: {self.y}")

        self.setXvel(x_vel)
        self.setYvel(y_vel)


human_spawnpoint = (0, 101)
ghost_spawnpoint = (380, 414)
