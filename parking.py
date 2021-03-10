from simulation import Vehicle
import numpy as np

class Parking() :
    def __init__(self, blocks):
        self.blocks = blocks
        self.occupation = dict()


class Block() :
    def __init__(self, lanes):
        self.lanes = lanes

class Lane() :
    def __init__(self, id_lane, length, top_access = True, bottom_access = True):
        self.length = length
        self.id = id_lane
        self.list_vehicles = np.array([None]*self.length)  
        self.length = length
        self.top_position = None                # indice de la premiere voiture occupée dans la lane (None si pas de voiture)
        self.bottom_position = None             # indice de la derniere voiture occupée dans la lane (None si pas de voiture)
        self.top_access = top_access
        self.bottom_access = bottom_access

    def push_top(self, id_vehicle):
        if self.top_position == None:
            if not self.bottom_access:
                self.list_vehicles[-1] = id_vehicle
                self.top_position = self.length - 1
                self.bottom_position = self.length -1
            else:
                self.list_vehicles[self.length//2] = id_vehicle
                self.top_position = self.length//2
                self.bottom_position = self.length//2
        else:
            self.list_vehicles[self.top_position-1] = id_vehicle
            self.top_position -= 1

    def pop_top(self):
        if self.top_position != None:
            self.list_vehicles[self.top_position] = None
            self.top_position += 1
            if self.top_position > self.bottom_position: #si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ca veut dire qu'il n'y a plus de voiture
                self.top_position = None
                self.bottom_position = None
    
    def push_bottom(self, id_vehicle):
        if self.bottom_position == None:
            if not self.top_access:
                self.list_vehicles[0] = id_vehicle
                self.top_position = 0
                self.bottom_position = 0
            else:
                self.list_vehicles[self.length//2] = id_vehicle
                self.top_position = self.length//2
                self.bottom_position = self.length//2
        else:
            self.list_vehicles[self.bottom_position + 1] = id_vehicle
            self.bottom_position += 1

    def pop_bottom(self):
        if self.bottom_position != None:
            self.list_vehicles[self.bottom_position] = None
            self.bottom_position -= 1
            if self.bottom_position < self.top_position: #si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ca veut dire qu'il n'y a plus de voiture
                self.bottom_position = None
                self.top_position = None

    def is_top_available(self):
        return self.top_access and (self.top_position == None or self.top_position != 0)

    def is_bottom_available(self):
        return self.bottom_access and (self.top_position == None or self.bottom_position != self.length - 1)

    


       

    
