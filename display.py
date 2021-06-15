import pygame as pg
import numpy as np
import datetime
import time
from sim_analysis import Analysis
import matplotlib.pyplot as plt
# plt.ion()

class Display():

    def __bool__(self):
        return True

    def __init__(self, simulation, place_width=15, place_length=20, time_interval=0.):
        self.stock = simulation.stock
        self.robots = simulation.robots
        self.t = simulation.t
        self.parking = simulation.parking
        self.place_length = place_length
        self.place_width = place_width

        self.last_update_day = 0

        self.simulation = simulation
        self.simulation.display = self
        if False:
            self.analysis = Analysis(self.simulation)
            self.figure = plt.figure()
        self.speed = 0
        self.time_interval = time_interval


        pg.init()
        self.screen = pg.display.set_mode((1200, 800))
        self.screen.fill((255, 255, 255))


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

        #On affiche Robot 1 :, Robot 2 : ...
        for i in range(4):
            text = self.font_fixed.render(f"Robot {i+1} :", True, (0, 0, 0))
            self.screen.blit(text, (900, i*70 + 40))

        pg.display.update()
    
        self.last_display_t = time.time()
    
    def run(self):
        
        clock = pg.time.Clock()

        running = True
        complete = False

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
                if time.time() - self.last_display_t > self.time_interval:
                    if self.speed == 0:
                        complete = self.simulation.next_event()[0]
                    if self.speed == 1:
                        complete = self.simulation.next_event(self.simulation.t + datetime.timedelta(minutes=15), None)[0]
                    if self.speed == 2:
                        complete = self.simulation.next_event(self.simulation.t.replace(minute=0, second=0) + datetime.timedelta(hours=1), None)[0]
                    if self.speed == 3:
                        complete = self.simulation.next_event(self.simulation.t.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1), None)[0]

        # Enfin on rajoute un appel à pg.quit()
        # Cet appel va permettre à pg de "bien s'éteindre" et éviter des bugs sous Windows
        pg.quit()
    
    def update(self):
        
        if time.time() - self.last_display_t > self.time_interval:

            self.last_display_t = time.time()

            pg.draw.rect(self.screen, (255, 255, 255), pg.Rect(900,10,300,30))
            t_surf = self.font_fixed.render(str(self.simulation.t), True, (0, 0, 0))
            self.screen.blit(t_surf, (900, 10))

            for vehicle_id in self.parking.occupation:
                self.draw_vehicle(self.stock.vehicles[vehicle_id])
            
            self.show_robot()
            
            pg.display.update()

            #on trace la figure de plt
            if False: #self.simulation.t.day != self.last_update_day:
                self.analysis.entree_vehicle()
                self.analysis.sortie_vehicle()
                self.analysis.count_vehicle()
                self.analysis.max_interface()
                self.analysis.flux()
                self.update_figure()
                self.figure.canvas.draw()
                self.last_update_day = self.simulation.t.day
    
    def shutdown(self):
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
        
        color1 = np.array([0,120,0])
        color2 = np.array([255,255,0])
        color3 = np.array([255,0,0])

        k = (vehicle.retrieval - self.simulation.t).total_seconds()
        if k >= 0:
            k = max(0,min(1,k/(86400*30)))**(1/3)
            color = color2 + k*(color1-color2)
        else:
            k = 0.5*max(0,min(1,-k/(86400)))**(1/3) + 0.5
            color = color2 + k*(color3-color2)
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
        if not self.speed:
            pg.display.update()

    def show_robot(self): 
        for i in range(4):
            rect3 = pg.Rect(990, i*70 + 40, 100 ,20) #recouvrement numéro de voiture
            rect4 = pg.Rect(900, i*70 + 60, 200, 30) #recouvrement jauge
            pg.draw.rect(self.screen, (255,255,255), rect3) #on actualise en couvrant avec un rectangle blanc
            pg.draw.rect(self.screen, (255,255,255), rect4)

        for i, x in enumerate(self.robots): #on parcourt tous les robots utilisés
            # pg.display.update()             
            if x.vehicle: #le robot transporte un véhicule
                text = self.font_fixed.render(f"{x.vehicle.id}", True, (0, 0, 0))
                self.screen.blit(text, (995, i*70 + 40)) #placement du texte

            if x.doing:
                #tracer le fond de la jauge proportionnelle à la durée de la tâche
                """
                print(x.doing)
                print(x.start_time)
                print(x.goal_time)
                """
                L = (x.goal_time - x.start_time)/datetime.timedelta(1,1)
                
                rect = pg.Rect(900, i*70 + 60, L*30000 + 100, 30)
                pg.draw.rect(self.screen, (0, 0, 0), rect)
            
                if x.start_time :
                    if x.goal_time > x.start_time:
                        pourc = 10# (self.simulation.t - x.start_time)/(x.goal_time - x.start_time)
                        rect2 = pg.Rect(900, i*70 + 60, pourc*(L*30000+100), 30)
                        pg.draw.rect(self.screen, (255, 0, 0), rect2) #tracer de la jauge
                    

    def update_figure(self):
        
        self.analysis.first_day, self.analysis.last_day = self.stock.duration_simu()
        n = (self.analysis.last_day - self.analysis.first_day).days
        t = [k for k in range(n)]
        plt.clf()

        plt.subplot(4,1,1)
        plt.plot(t, [0]*n, color='white') #permet de tracer la fenêtre aux bonnes dimensions
        plt.plot(self.analysis.nb_entree_array, label="Nombre d'entrées")
        plt.plot(self.analysis.nb_sortie_array, label="Nombre de sorties")
        plt.ylabel('Nombre de voitures')
        plt.legend()

        plt.subplot(4,1,2)
        plt.plot(t, [1] + [0]*(n-1), color='white')
        plt.plot(self.analysis.taux_occupation_array, label="Taux d'occupation du parking")
        plt.legend()

        plt.subplot(4,1,3)
        plt.plot(t, [1] + [0]*(n-1), color='white')
        plt.plot(self.analysis.nb_vehicles_interface_array, label="Occupation maximale de l'interface")
        plt.legend()

        plt.subplot(4,1,4)
        plt.plot(t, [0]*n, color='white')
        plt.plot(self.analysis.flux_moyen_array)
        plt.xlabel('Jour')
        plt.ylabel("Flux moyen")