import pygame.image
import pygame
from time import time
from shapely.geometry import box
from typing import Dict

pygame.init()


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

        self._actionkeyson: Dict[str, any] = {
            "movement": {
                "xaxis": {pygame.K_a: lambda: self.setXvel(-self.speed),
                          pygame.K_d: lambda: self.setXvel(self.speed)},

                "yaxis": {pygame.K_w: lambda: self.setYvel(-self.speed),
                          pygame.K_s: lambda: self.setYvel(self.speed)}
            }
        }
        self._actionkeysoff: Dict[str, any] = {
            "movement": {
                "xaxis": {pygame.K_a: lambda: self.setXvel(0),
                          pygame.K_d: lambda: self.setXvel(0)},

                "yaxis": {pygame.K_w: lambda: self.setYvel(0),
                          pygame.K_s: lambda: self.setYvel(0)}
            }
        }

    def execEvents(self):
        keys = pygame.key.get_pressed()

        for axis in self._actionkeyson["movement"]:
            for key in self._actionkeyson["movement"][axis]:
                if keys[key]:
                    self._actionkeyson["movement"][axis][key]()
                    break
                else:
                    self._actionkeysoff["movement"][axis][key]()

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

    def getCors(self):
        return self.x, self.y

    def updateBox(self):
        self.box = box(self.x, self.y, self.x + self.width, self.y + self.height)

    def isHuman(self):
        return type(self).__name__ == 'Human'

    def isGhost(self):
        return not self.isHuman()


class Human(Player):
    def __init__(self, stx, sty, flash_mode, rotation, lives):
        super().__init__("man.png", stx, sty)  # Inherits from player class
        self.rotation = rotation
        self.flash_mode = flash_mode
        self.lives = lives

        _playerkeysoff = {
            "flashlight": {pygame.K_SPACE: lambda state: self.flashlight(state)}
        }
        _playerkeyson = {
            "flashlight": {pygame.K_SPACE: lambda state: self.flashlight(state)}
        }
        self._actionkeyson.update(_playerkeyson)
        self._actionkeysoff.update(_playerkeysoff)

    def flashlight(self, state):
        if state:
            self.flash_mode = "on"
        else:
            self.flash_mode = "off"

    def execEvents(self):
        super().execEvents()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            self._actionkeyson["flashlight"][pygame.K_SPACE](True)
        else:
            self._actionkeysoff["flashlight"][pygame.K_SPACE](False)


class Ghost(Player):

    def __init__(self, stx, sty, health, timer, burning, visible):
        super().__init__("ghost (1).png", stx, sty)  # Inherits from player class
        self.health = health
        self.timer = timer
        self.burning = burning
        self.visible = visible

        _playerkeysoff = {
            "dash": {pygame.K_SPACE: lambda dashing: self.dash(dashing)}
        }
        _playerkeyson = {
            "dash": {pygame.K_SPACE: lambda dashing: self.dash(dashing)}
        }
        self._actionkeyson.update(_playerkeyson)
        self._actionkeysoff.update(_playerkeysoff)

    def burn(self):
        self.timer = time()
        self.burning = True
        self.visible = True
        self.speed = 7

    def dash(self, dashing):
        if dashing:
            self.speed = 8
            self.visible = True
        else:
            self.speed = 5
            if not self.burning:
                self.visible = False

    def execEvents(self):
        super().execEvents()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            self._actionkeyson["dash"][pygame.K_SPACE](True)
        else:
            self._actionkeysoff["dash"][pygame.K_SPACE](False)


human_spawnpoint = (0, 100)
ghost_spawnpoint = (100, 200)
default_players = [Human(human_spawnpoint[0], human_spawnpoint[1], flash_mode="off", rotation=0, lives=3),
                   Ghost(ghost_spawnpoint[0], ghost_spawnpoint[1], health=100, timer=time(), burning=False,
                         visible=False)]
