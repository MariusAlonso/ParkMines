import pygame as pg
from simulation import *
import numpy as np
from sim_analysis import Analysis
import matplotlib.pyplot as plt
plt.ion()

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

        self.last_update_day = 0

        self.simulation = Simulation(t0, stock, robots, parking, AlgorithmType, print_in_terminal, self)
        self.analysis = Analysis(self.simulation)
        self.speed = 0
        self.time_interval = 0

        pg.init()
        self.screen = pg.display.set_mode((1200, 800))
        self.screen.fill((255, 255, 255))
        clock = pg.time.Clock()

        self.figure = plt.figure()

        max_i_disposal = len(self.parking.disposal)
        max_j_disposal = len(self.parking.disposal[0])
        x0 = [20]*max_j_disposal
        y0 = [20]*max_i_disposal

        #print(self.parking.disposal)

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

        print(self.parking.disposal)

        for j_disposal in range(1, max_j_disposal):   

            for i_disposal in range(max_i_disposal):

                block_id = self.parking.disposal[i_disposal][j_disposal]

                if self.parking.disposal[i_disposal][j_disposal-1] != block_id:
                    k = j_disposal - 1
                    while k >=0 and self.parking.disposal[i_disposal][k] == self.parking.disposal[i_disposal][j_disposal-1]:
                        k -= 1

                    block_id = self.parking.disposal[i_disposal][k+1]
                    if type(block_id) == str or self.parking.blocks[block_id].direction == "topbottom":
                        x0[j_disposal] = max(x0[j_disposal], x0[k+1] + self.block_width(block_id))
                    else:
                        x0[j_disposal] = max(x0[j_disposal], x0[k+1] + self.block_height(block_id))
                
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

        self.x0 = x0
        self.y0 = y0
        #print(x0, y0)
        self.font = pg.font.SysFont(None, 2*self.place_length//4)
        self.font_fixed = pg.font.SysFont(None, 30)
        """
        text_input_box = TextInputBox(50, 50, 400, font)
        group = pg.sprite.Group(text_input_box)
        """

        #On affiche Robot 1 :, Robot 2 : ...
        for i in range(4):
            text = self.font_fixed.render(f"Robot {i+1} :", True, (0, 0, 0))
            self.screen.blit(text, (700, i*70 + 40))


        running = True
        complete = False
        last_display_t = time.time()

        while running:
            clock.tick(100)

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

                    if event.key == pg.K_s:
                        self.speed += 1
                        self.speed %= 4
            if complete:
                if time.time() - last_display_t > self.time_interval:
                    if self.speed == 0:
                        complete = self.simulation.next_event()
                    if self.speed == 1:
                        complete = self.simulation.next_event(self.simulation.t + datetime.timedelta(minutes=15))
                    if self.speed == 2:
                        complete = self.simulation.next_event(self.simulation.t.replace(minute=0, second=0) + datetime.timedelta(hours=1))
                    if self.speed == 3:
                        complete = self.simulation.next_event(self.simulation.t.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1))
                    last_display_t = time.time()      
           
            #self.screen.fill(0)
            """
            group.update(event_list)
            group.draw(self.screen)
            """
            pg.draw.rect(self.screen, (255, 255, 255), pg.Rect(900,10,300,30))
            t_surf = self.font_fixed.render(str(self.simulation.t), True, (0, 0, 0))
            self.screen.blit(t_surf, (900, 10))

            for vehicle_id in self.parking.occupation:
                self.draw_vehicle(self.stock.vehicles[vehicle_id])  

            pg.display.update()

            #on trace la figure de plt
            if self.simulation.t.day != self.last_update_day:
                self.analysis.entree_vehicle()
                self.analysis.sortie_vehicle()
                self.analysis.count_vehicle()
                self.analysis.count_vehicle_interface()
                self.analysis.flux()
                self.update_figure()
                self.figure.canvas.draw()
                self.last_update_day = self.simulation.t.day

        # Enfin on rajoute un appel à pg.quit()
        # Cet appel va permettre à pg de "bien s'éteindre" et éviter des bugs sous Windows
        pg.quit()
    
    def block_width(self, block_id):
        if block_id == "s":
            return self.place_width
        if block_id == "l":
            return 7*self.place_width
        elif block_id == "e":
            return 0
        elif type(block_id) == str and block_id[0] == "f":
            return int(block_id[1:].split(":")[0])*self.place_width
        return (len(self.parking.blocks[block_id].lanes)+1)*(self.place_width+1)

    def block_height(self, block_id):
        if block_id == "s":
            return self.place_width
        if block_id == "l":
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

        if self.simulation.t < vehicle.order_retrieval:
            color = (75,200,0)
        else:
            k = (vehicle.retrieval - self.simulation.t).total_seconds()/86400
            if k >= 0:
                color = (max(150-k*150/30,0),min(150+k*100/30,255),0)
            else:
                color = (min(255,150-24*k*100),max(0,150+24*k*150,0),0)
        pg.draw.rect(self.screen, color, rect)
        
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
        for i in range(4):
            rect3 = pg.Rect(790, i*70 + 40, 100 ,20) #recouvrement numéro de voiture
            rect4 = pg.Rect(700, i*70 + 60, 200, 30) #recouvrement jauge
            pg.draw.rect(self.screen, (255,255,255), rect3) #on actualise en couvrant avec un rectangle blanc
            pg.draw.rect(self.screen, (255,255,255), rect4)

        for i, x in enumerate(self.robots): #on parcourt tous les robots utilisés
            # pg.display.update()             
            if x.vehicle: #le robot transporte un véhicule
                if x.target: #le robot a une cible en tête
                    text = self.font_fixed.render(f"{x.vehicle.id}", True, (0, 0, 0))
                    self.screen.blit(text, (795, i*70 + 40)) #placement du texte

                #tracer le fond de la jauge proportionnelle à la durée de la tâche
                L = (x.goal_time - x.start_time)/datetime.timedelta(1,1)
                
                rect = pg.Rect(700, i*70 + 60, L*30000 + 100, 30)
                pg.draw.rect(self.screen, (0, 0, 0), rect)
            
                if x.start_time :
                    if x.goal_time > x.start_time:
                        pourc = (self.simulation.t - x.start_time)/(x.goal_time - x.start_time)
                        rect2 = pg.Rect(700, i*70 + 60, pourc*(L*30000+100), 30)
                        pg.draw.rect(self.screen, (255, 0, 0), rect2) #tracer de la jauge
            pg.display.update()

    def update_figure(self):
        
        self.analysis.first_day, self.analysis.last_day = self.stock.duration_simu()
        n = (self.analysis.last_day - self.analysis.first_day).days
        t = [k for k in range(n)]
        plt.clf()

        plt.subplot(3,1,1)
        plt.plot(t, [0]*n, color='white') #permet de tracer la fenêtre aux bonnes dimensions
        plt.plot(self.analysis.nb_entree_array, label="Nombre d'entrées")
        plt.plot(self.analysis.nb_sortie_array, label="Nombre de sorties")
        plt.ylabel('Nombre de voitures')
        plt.legend()

        plt.subplot(3,1,2)
        plt.plot(t, [1] + [0]*(n-1), color='white')
        plt.plot(self.analysis.taux_occupation_array, label="Taux d'occupation du parking")
        plt.plot(self.analysis.taux_occupation_interface_array, label="Taux d'occupation de l'interface")
        plt.legend()

        plt.subplot(3,1,3)
        plt.plot(t, [0]*n, color='white')
        plt.plot(self.analysis.flux_moyen_array)
        plt.xlabel('Jour')
        plt.ylabel("Flux moyen")