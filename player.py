from math import sqrt
import pygame.image
import pygame
from time import time
from shapely.geometry import box
from typing import Dict

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
        self.speed = 5
        self.rotation = 0

        self._actionkeys: Dict[str, any] = {
            "movement": {
                "xaxis": {pygame.K_a: lambda speed: self.setXvel(-speed),
                          pygame.K_d: lambda speed: self.setXvel(speed)},

                "yaxis": {pygame.K_w: lambda speed: self.setYvel(-speed),
                          pygame.K_s: lambda speed: self.setYvel(speed)}
            }
        }
        # self._actionkeysoff: Dict[str, any] = {
        #     "movement": {
        #         "xaxis": {pygame.K_a: lambda: self.setXvel(0),
        #                   pygame.K_d: lambda: self.setXvel(0)},
        #
        #         "yaxis": {pygame.K_w: lambda: self.setYvel(0),
        #                   pygame.K_s: lambda: self.setYvel(0)}
        #     }
        # }

    def execEvents(self):
        keys = pygame.key.get_pressed()

        for axis in self._actionkeys["movement"]:
            for key in self._actionkeys["movement"][axis]:
                if keys[key]:
                    self._actionkeys["movement"][axis][key](self.speed)
                    break
                else:
                    self._actionkeys["movement"][axis][key](0)

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
        super().__init__("images/man.png", stx, sty)  # Inherits from player class
        self.rotation = 0
        self.flash_mode = "off"
        self.lives = 3

        _playerkeys = {
            "flashlight": {pygame.K_SPACE: lambda state: self.flashlight(state)}
        }
        self._actionkeys.update(_playerkeys)

    def flashlight(self, state):
        if state:
            self.flash_mode = "on"
        else:
            self.flash_mode = "off"

    def execEvents(self):
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
        self.timer = time()
        self.burning = True
        self.visible = True
        self.speed = 7

    def dash(self, d):
        if d:
            if not self.dashing:
                self.speed = 8
                self.dashing = True
                self.visible = True
                pygame.mixer.Sound.play(ghost_dash)
        else:
            self.dashing = False
            if not self.burning:
                self.visible = False
                self.speed = 5

    def execEvents(self):
        super().execEvents()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            self._actionkeys["dash"][pygame.K_SPACE](True)
        else:
            self._actionkeys["dash"][pygame.K_SPACE](False)


human_spawnpoint = (0, 101)
ghost_spawnpoint = (100, 200)
default_players = [Human(human_spawnpoint[0], human_spawnpoint[1]),
                   Ghost(ghost_spawnpoint[0], ghost_spawnpoint[1])]
