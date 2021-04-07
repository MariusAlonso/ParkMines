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

    def __bool__(self):
        return True

    def __init__(self, t0, stock, robots, parking, AlgorithmType, place_width=15, place_length=20, print_in_terminal=False):
        self.stock = stock
        self.robots = robots
        self.t = t0
        self.parking = parking
        self.place_length = place_length
        self.place_width = place_width

        self.simulation = Simulation(t0, stock, robots, parking, AlgorithmType, print_in_terminal, self)


        pg.init()
        self.screen = pg.display.set_mode((1000, 800))
        self.screen.fill((255, 255, 255))
        clock = pg.time.Clock()

        max_i_disposal = len(self.parking.disposal)
        max_j_disposal = len(self.parking.disposal[0])
        x0 = [0]*max_j_disposal
        y0 = [0]*max_i_disposal

        print(self.parking.disposal)

        for i_disposal in range(1, max_i_disposal):   

            for j_disposal in range(max_j_disposal):

                block_id = self.parking.disposal[i_disposal][j_disposal]

                if self.parking.disposal[i_disposal-1][j_disposal] != block_id:
                    k = i_disposal - 1
                    while k >=0 and self.parking.disposal[k][j_disposal] == self.parking.disposal[i_disposal-1][j_disposal]:
                        k -= 1

                    block_id = self.parking.disposal[k+1][j_disposal]
                    if type(block_id) == str or self.parking.blocks[block_id].direction == "topbottom":
                        y0[i_disposal] = max(y0[i_disposal], y0[k+1] + self.block_height(block_id))
                    else:
                        y0[i_disposal] = max(y0[i_disposal], y0[k+1] + self.block_width(block_id))

                print("y0",y0)

        for j_disposal in range(1, max_j_disposal):   

            for i_disposal in range(max_i_disposal):

                block_id = self.parking.disposal[i_disposal][j_disposal]

                if self.parking.disposal[i_disposal][j_disposal-1] != block_id:
                    k = j_disposal - 1
                    while k >=0 and self.parking.disposal[i_disposal][k] == self.parking.disposal[i_disposal][j_disposal-1]:
                        k -= 1

                    block_id = self.parking.disposal[k+1][j_disposal]
                    if type(block_id) == str or self.parking.blocks[block_id].direction == "topbottom":
                        x0[j_disposal] = max(x0[j_disposal], x0[k+1] + self.block_width(block_id))
                    else:
                        y0[i_disposal] = max(y0[i_disposal], y0[k+1] + self.block_height(block_id))
                
                print("x0",x0)
        
        for i_disposal, list_block_id in enumerate(self.parking.disposal):
            
            for j_disposal, block_id in enumerate(list_block_id):

                if type(block_id) == str:
                    continue

                if j_disposal and block_id == self.parking.disposal[i_disposal][j_disposal-1]:
                    print(i_disposal, j_disposal)
                    continue

                if i_disposal and block_id == self.parking.disposal[i_disposal-1][j_disposal]:
                    print("i", i_disposal, j_disposal)
                    continue

                self.parking.blocks[block_id].x_pos = x0[j_disposal]
                self.parking.blocks[block_id].y_pos = y0[i_disposal]
                
                nb_lanes = len(self.parking.blocks[block_id].lanes)
                lane_length = self.parking.blocks[block_id].lanes[0].length
                block_width = nb_lanes*(place_width+1)+1
                block_height = lane_length*(place_length+1)+1


                
                if self.parking.blocks[block_id].direction == "topbottom":

                    rect = pg.Rect(x0[j_disposal], y0[i_disposal], block_width, block_height)
                    pg.draw.rect(self.screen, (100, 100, 100), rect)

                    x = x0[j_disposal]
                    for i in range(nb_lanes+1):
                        pg.draw.line(self.screen, (0, 0, 0), (x, y0[i_disposal]), (x, y0[i_disposal]+block_height-1))
                        x += place_width+1

                    y = y0[i_disposal]
                    for j in range(lane_length+1):
                        pg.draw.line(self.screen, (0, 0, 0), (x0[j_disposal], y), (x0[j_disposal]+block_width-1, y))
                        y += place_length+1

                else:
                    
                    rect = pg.Rect(x0[j_disposal], y0[i_disposal], block_height, block_width)
                    pg.draw.rect(self.screen, (100, 100, 100), rect)

                    x = x0[j_disposal]
                    for i in range(lane_length+1):
                        pg.draw.line(self.screen, (0, 0, 0), (x, y0[i_disposal]), (x, y0[i_disposal]+block_width-1))
                        x += place_length+1

                    y = y0[i_disposal]
                    for j in range(nb_lanes+1):
                        pg.draw.line(self.screen, (0, 0, 0), (x0[j_disposal], y), (x0[j_disposal]+block_height-1, y))
                        y += place_width+1


        self.font = pg.font.SysFont(None, 2*self.place_length//4)
        self.font_fixed = pg.font.SysFont(None, 30)
        """
        text_input_box = TextInputBox(50, 50, 400, font)
        group = pg.sprite.Group(text_input_box)
        """

        running = True
        complete = False

        while running:
            clock.tick(1000)

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

                    if event.key == pg.K_RETURN:
                        self.simulation.next_event()

                    if event.key == pg.K_c:
                        complete = not complete
            
            if complete:
                complete = self.simulation.next_event()
            
            #self.screen.fill(0)
            """
            group.update(event_list)
            group.draw(self.screen)
            """
            pg.draw.rect(self.screen, (255, 255, 255), pg.Rect(700,10,300,30))
            t_surf = self.font_fixed.render(str(self.simulation.t), True, (0, 0, 0))
            self.screen.blit(t_surf, (700, 10))

            pg.display.update()

        # Enfin on rajoute un appel à pg.quit()
        # Cet appel va permettre à pg de "bien s'éteindre" et éviter des bugs sous Windows
        pg.quit()
    
    def block_width(self, block_id):
        if block_id == "s":
            return self.place_width
        elif block_id == "e":
            return 0
        elif type(block_id) == str and block_id[0] == "f":
            return int(block_id[1:].split(":")[0])*self.place_width
        return (len(self.parking.blocks[block_id].lanes)+1)*(self.place_width+1)

    def block_height(self, block_id):
        if block_id == "s":
            return self.place_width
        elif block_id == "e":
            return 0
        elif type(block_id) == str and block_id[0] == "f":
            return int(block_id[1:].split(":")[1])*self.place_width
        return self.parking.blocks[block_id].lanes[0].length*(self.place_length+1) + 1 + self.place_width

    def draw_vehicle(self, vehicle):
        block_id, lane_id, position = self.parking.occupation[vehicle.id]
        x_block = self.parking.blocks[block_id].x_pos
        y_block = self.parking.blocks[block_id].y_pos
        if self.parking.blocks[block_id].direction == "topbottom":
            x = x_block + (self.place_width+1)*lane_id + (self.place_width - 3*self.place_width//4)//2 + 1
            y = y_block + (self.place_length+1)*position + (self.place_width - 3*self.place_width//4)//2 + 1
            rect = pg.Rect(x, y, 3*self.place_width//4, 3*self.place_length//4)
        else:
            x = x_block + (self.place_length+1)*position + (self.place_width - 3*self.place_width//4)//2 + 1
            y = y_block + (self.place_width+1)*lane_id + (self.place_width - 3*self.place_width//4)//2 + 1
            rect = pg.Rect(x, y, 3*self.place_length//4, 3*self.place_width//4)           
        pg.draw.rect(self.screen, (200, 0, 0), rect)
        
        # Affichage de l'identifiant du véhicule
        t_surf = self.font.render(str(vehicle.id), True, (0, 0, 0))
        self.screen.blit(t_surf, (x, y))


    def erase_vehicle(self, vehicle):
        block_id, lane_id, position = self.parking.occupation[vehicle.id]
        x_block = self.parking.blocks[block_id].x_pos
        y_block = self.parking.blocks[block_id].y_pos
        if self.parking.blocks[block_id].direction == "topbottom":
            x = x_block + (self.place_width+1)*lane_id + 1
            y = y_block + (self.place_length+1)*position + 1
            rect = pg.Rect(x, y, self.place_width, self.place_length)
        else:
            x = x_block + (self.place_length+1)*position + 1
            y = y_block + (self.place_width+1)*lane_id + 1
            rect = pg.Rect(x, y, self.place_length, self.place_width)           
        pg.draw.rect(self.screen, (100, 100, 100), rect)

    def show_robot(self):
        pass
        """
        for i, x in enumerate(self.robots):
            rect3 = pg.Rect(700, 40, 200 ,800)
            pg.draw.rect(self.screen, (255,255,255), rect3)
            if x.target:
                text = self.font_fixed.render(f"Robot {x.id_robot} : {x.target.vehicle.id}", True, (0, 0, 0))
                self.screen.blit(text, (700, 40)) #placement du texte

            #tracer de la jauge d'avancement de l'event
            rect = pg.Rect(700, (i+1)*15 + 80, 100, 30)
            pg.draw.rect(self.screen, (0, 0, 0), rect)
            
            if x.start_time :
                print (x.goal_time, x.start_time, self.simulation.t)
                if x.goal_time > x.start_time: #self.t ne s'actualise pas
                    pourc = (self.t - x.start_time)/(x.goal_time - x.start_time)
                    print(pourc)
                    rect2 = pg.Rect(700, (i+1)*15 + 80, pourc*100, 30)
                    pg.draw.rect(self.screen, (255, 0, 0), rect2)
        """
                
