import pygame as pg
from simulation import *
import numpy as np


"""
FICHIER A SUPPRIMMER
"""







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


class Display():

    def __init__(self, t0, stock, nb_robots, parking, AlgorithmType, place_width, place_length):
        self.stock = stock
        self.nb_robots = nb_robots
        self.t = t0
        self.parking = parking
        self.place_width = place_width
        self.place_length = place_length

        self.simulation = Simulation(t0, stock, nb_robots, parking, AlgorithmType)


        pg.init()
        self.screen = pg.display.set_mode((1000, 700))
        clock = pg.time.Clock()

        for list_block_id in enumerate(self.parking.disposal):

            for block_id in list_block_id:
                nb_lanes = len(block_id.lanes)
                lane_length = block_id.lanes.length
                block_width = nb_lanes*(place_width+1)+1
                block_height = lane_length*(place_length+1)+1

                rect = Rect(x, y, block_width, block_height)
                pg.draw.rect(self.screen, (100, 100, 100), rect)

                for i in range(nb_lanes+1):
                    pg.draw.line(self.screen, (0, 0, 0), (x, y), (x, y+block_height-1))
                    x += place_width+1

                for j in range(lane_length+1):
                    pg.draw.line(self.screen, (0, 0, 0), (x-block_width, y), (x-1, y))
                    y += place_length+1
                
                y -= block_height+place_length
            
            x = place_width + 1
            y += block_height+place_width

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



            pg.display.update()

        # Enfin on rajoute un appel à pg.quit()
        # Cet appel va permettre à pg de "bien s'éteindre" et éviter des bugs sous Windows
        pg.quit()