import pygame
from shapely.geometry import box, Point


class Block:

    def __init__(self, x1, y1, x2, y2, color):
        # Make sure x2 and y2 are the greater values
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.width = x2 - x1
        self.height = y2 - y1
        self.rect = pygame.Rect(x1, y1, self.width, self.height)
        self.block_box = box(x1 + 1, y1 + 1, x2 - 1, y2 - 1)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


