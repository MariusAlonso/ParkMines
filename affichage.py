import pygame as pg
from simulation import *

class TextInputBox(pg.sprite.Sprite):

    def __init__(self, x, y, w, font):
        super().__init__()
        self.color = (255, 255, 255)
        self.backcolor = None
        self.pos = (x, y) 
        self.width = w
        self.font = font
        self.active = False
        self.text = ""
        self.render_text()

    def render_text(self):
        t_surf = self.font.render(self.text, True, self.color, self.backcolor)
        self.image = pg.Surface((max(self.width, t_surf.get_width()+10), t_surf.get_height()+10), pg.SRCALPHA)
        if self.backcolor:
            self.image.fill(self.backcolor)
        self.image.blit(t_surf, (5, 5))
        pg.draw.rect(self.image, self.color, self.image.get_rect().inflate(-2, -2), 2)
        self.rect = self.image.get_rect(topleft = self.pos)

    def update(self, event_list):
        for event in event_list:
            if event.type == pg.MOUSEBUTTONDOWN and not self.active:
                self.active = self.rect.collidepoint(event.pos)
            if event.type == pg.KEYDOWN and self.active:
                if event.key == pg.K_RETURN:
                    self.active = False
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.render_text()

pg.init()
screen = pg.display.set_mode((1000, 700))
clock = pg.time.Clock()

font = pg.font.SysFont(None, 30)
text_input_box = TextInputBox(50, 50, 400, font)
group = pg.sprite.Group(text_input_box)

running = True

while running:
    clock.tick(10)

    # on itère sur tous les évênements qui ont eu lieu depuis le précédent appel
    # ici donc tous les évènements survenus durant la seconde précédente
    event_list = pg.event.get()

    for event in event_list:
        # chaque évênement à un type qui décrit la nature de l'évênement
        # un type de pg.QUIT signifie que l'on a cliqué sur la "croix" de la fenêtre
        if event.type == pg.QUIT:
            running = False
        # un type de pg.KEYDOWN signifie que l'on a appuyé une touche du clavier
        elif event.type == pg.KEYDOWN:

            if event.key == pg.K_UP:
                pass
    
    screen.fill(0)
    group.update(event_list)
    group.draw(screen)


    pg.draw.circle(screen, (0, 255, 0), (25, 25), 25)



    pg.display.update()

# Enfin on rajoute un appel à pg.quit()
# Cet appel va permettre à pg de "bien s'éteindre" et éviter des bugs sous Windows
pg.quit()