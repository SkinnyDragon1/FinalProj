import pygame


class Button:
    def __init__(self, text, x, y, w, h, color, fontsize, myfunc):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = w
        self.height = h
        self.fontsize = fontsize
        self.func = myfunc

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", self.fontsize)
        text = font.render(self.text, True, (255, 255, 255))
        screen.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                           self.y + round(self.height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            self.func()
        else:
            return False

    def check_hover(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            self.color = (133, 117, 115)
        else:
            self.color = (89, 78, 77)
