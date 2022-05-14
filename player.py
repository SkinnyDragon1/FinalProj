import pygame.image
# import game
from time import perf_counter

class Player:
    def __init__(self, img, stx, sty):
        self.img = img
        self.width = pygame.image.load(self.img).get_width()
        self.height = pygame.image.load(self.img).get_height()
        self.x = stx
        self.y = sty
        self.x_vel = 0
        self.y_vel = 0
        self.speed = 5
        self.rotation = 0

    def show(self, screen):
        screen.blit(pygame.image.load(self.img), (self.x, self.y))

    def addX(self, a):
        self.x += a

    def addY(self, a):
        self.y += a

    def setCors(self, x, y):
        self.x = x
        self.y = y

    def getCors(self):
        return self.x, self.y

    def isHuman(self):
        return type(self).__name__ == 'Human'

    def isGhost(self):
        return type(self).__name__ == 'Ghost'


class Human(Player):

    def __init__(self, img, stx, sty, flash_mode, rotation, lives):
        super().__init__(img, stx, sty)
        self.rotation = rotation
        self.flash_mode = flash_mode
        self.lives = lives


class Ghost(Player):

    def __init__(self, img, stx, sty, health, timer, burning):
        super().__init__(img, stx, sty) # Inherits from player class
        self.health = health
        self.timer = timer
        self.burning = burning

    def burn(self):
        self.timer = perf_counter()
        self.burning = True

