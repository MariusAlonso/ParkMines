import pygame as pg
from simulation import *
import numpy as np

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

    def __init__(self, t0, stock, nb_robots, parking, AlgorithmType, place_width=15, place_length=20):
        self.stock = stock
        self.nb_robots = nb_robots
        self.t = t0
        self.parking = parking
        self.place_length = place_length
        self.place_width = place_width

        self.simulation = Simulation(t0, stock, nb_robots, parking, AlgorithmType)


        pg.init()
        self.screen = pg.display.set_mode((1000, 700))
        self.screen.fill((255, 255, 255))
        clock = pg.time.Clock()

        max_i_disposal = len(self.parking.disposal)
        max_j_disposal = len(self.parking.disposal[0])
        x0 = [0]*max_i_disposal
        y0 = [0]*max_j_disposal

        for i_disposal in range(1, max_i_disposal):   

            for j_disposal in range(max_j_disposal):

                block_id = self.parking.disposal[i_disposal][j_disposal]

                if self.parking.disposal[i_disposal-1][j_disposal] != block_id:
                    k = i_disposal - 1
                    while k >=0 and self.parking.disposal[k][j_disposal] == self.parking.disposal[i_disposal-1][j_disposal]:
                        k -= 1
                    y0[i_disposal] = max(y0[i_disposal], y0[k] + self.block_height(self.parking.disposal[k][j_disposal]))

            print("y0",y0)

        for j_disposal in range(1, max_j_disposal):   

            for i_disposal in range(max_i_disposal):

                block_id = self.parking.disposal[i_disposal][j_disposal]

                if self.parking.disposal[i_disposal][j_disposal-1] != block_id:
                    k = j_disposal - 1
                    while k >=0 and self.parking.disposal[i_disposal][k] == self.parking.disposal[i_disposal][j_disposal-1]:
                        k -= 1
                    print("x0",x0)
                    x0[j_disposal] = max(x0[j_disposal], x0[k] + self.block_width(self.parking.disposal[i_disposal][k]))
        
        for i_disposal, list_block_id in enumerate(self.parking.disposal):
            
            for j_disposal, block_id in enumerate(list_block_id):

                if block_id in ["e", "s"] :
                    continue
                
                nb_lanes = len(self.parking.blocks[block_id].lanes)
                lane_length = self.parking.blocks[block_id].lanes[0].length
                block_width = nb_lanes*(place_width+1)+1
                block_height = lane_length*(place_length+1)+1

                rect = pg.Rect(x0[i_disposal], y0[j_disposal], block_width, block_height)
                pg.draw.rect(self.screen, (100, 100, 100), rect)
                

                x = x0[i_disposal]
                for i in range(nb_lanes+1):
                    pg.draw.line(self.screen, (0, 0, 0), (x, y0[j_disposal]), (x, y0[j_disposal]+block_height-1))
                    x += place_width+1

                y = y0[j_disposal]
                for j in range(lane_length+1):
                    pg.draw.line(self.screen, (0, 0, 0), (x0[i_disposal], y), (x0[i_disposal]+block_width-1, y))
                    y += place_length+1

                print(x0,y0)


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
            
            #self.screen.fill(0)
            group.update(event_list)
            group.draw(self.screen)



            pg.display.update()

        # Enfin on rajoute un appel à pg.quit()
        # Cet appel va permettre à pg de "bien s'éteindre" et éviter des bugs sous Windows
        pg.quit()
    
    def block_width(self, block_id):
        if block_id == "s":
            return self.place_width
        if block_id == "e":
            return 0
        return (len(self.parking.blocks[block_id].lanes)+1)*(self.place_width+1)

    def block_height(self, block_id):
        if block_id == "s":
            return self.place_width
        if block_id == "e":
            return 0
        return self.parking.blocks[block_id].lanes[0].length*(self.place_length+1) + 1 + self.place_width