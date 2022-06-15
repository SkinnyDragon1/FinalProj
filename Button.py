import pygame

pygame.font.init()

width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Luigi's Ghost Mansion")
luigibg = pygame.image.load("images/luigibg.png")
ghostbg = pygame.image.load("images/ghostbg1.png")
icon = pygame.image.load("images/game_icon.png")
pygame.display.set_icon(icon)


class Button:
    def __init__(self, text, x, y, w, h, color, fontsize):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = w
        self.height = h
        self.fontsize = fontsize

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", self.fontsize)
        text = font.render(self.text, True, (255, 255, 255))
        screen.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                           self.y + round(self.height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            print(self.text)
        else:
            return False

    def checkHover(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            self.color = (133, 117, 115)
        else:
            self.color = (89, 78, 77)


btns = [Button("How to Play", 250, 300, 300, 150, (89, 78, 77), 50),
        Button("Singleplayer", 250, 460, 145, 72.5, (89, 78, 77), 20),
        Button("Multiplayer", 405, 460, 145, 72.5, (89, 78, 77), 20)
        ]


def main():
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
            btn.checkHover(pos)
            btn.draw(screen)

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
