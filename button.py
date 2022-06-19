import pygame


class Button:
    def __init__(self, text, x, y, w, h, color, hover_color, fontsize, myfunc):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.hover_color = hover_color
        self.width = w
        self.height = h
        self.fontsize = fontsize
        self.func = myfunc

    def draw(self, screen, mouse_pos):
        if self.check_hover(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, (self.x, self.y, self.width, self.height))
        else:
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
            return True
        else:
            return False
