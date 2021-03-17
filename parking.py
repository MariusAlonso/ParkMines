from simulation import Vehicle
import numpy as np
import datetime

class Parking():
    def __init__(self, blocks, disposal=[[]]):
        self.blocks = blocks
        self.occupation = dict()
        self.disposal = disposal
<<<<<<< HEAD
        self.access = access
        self.nb_of_places = self.nbOfPlaces()
=======
>>>>>>> 74351b0dc8a02cead45d41407d0fb4b0b52f23e2
    
    def __repr__(self):
        return self.blocks[0].__repr__()
    
<<<<<<< HEAD
    def nbOfPlaces(self):
        return sum(block.height*block.width for block in self.blocks)
=======
    def travel_time(self, departure, arrival):
        return 0.1 #datetime.timedelta(0,0,0,0,15)
>>>>>>> 74351b0dc8a02cead45d41407d0fb4b0b52f23e2


class Block():
    def __init__(self, lanes):
        self.lanes = lanes
    
    def __repr__(self):
        # on représente les lanes horizontalement pour construire et on transpose avant d'afficher
        height = len(self.lanes) # en nombre de voitures
        width = self.lanes[0].length # en nombre de voitures
        matrix = np.empty((height, width), dtype='<U5')
        for row_index, lane in enumerate(self.lanes):
            liste = lane.list_vehicles[:]
            liste = [str(item).replace('None', '-') for item in liste]
            matrix[row_index] = liste

        # les lanes sont les colonnes (la première à gauche)
        # conformément aux termes top et bottom pour les extrémités
        return matrix.__repr__()

class BlockInterface(Block):

    def empty_lane(self): #renvoie "full" si interface est pleine, et return premier vehicule
        for i_lane, lane in enumerate(self.lanes):
            if lane.list_vehicles[0] == None:
                return i_lane
        else:
            return "full"

    def occupied_lane(self): #renvoie "empty" si interface est pleine, et return premier vehicule
        for i_lane, lane in enumerate(self.lanes):
            if lane.list_vehicles[0] != None:
                return i_lane
        else:
            return "empty"



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

    def __repr__(self):
        liste = self.list_vehicles[:]
        liste = [str(item).replace('None', '-') for item in liste]
        return liste.__repr__()

    def push_top(self, id_vehicle, coté):
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
            vehicle_id = self.list_vehicles[self.top_position]
            self.list_vehicles[self.top_position] = None
            self.top_position += 1
            if self.top_position > self.bottom_position: # si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ca veut dire qu'il n'y a plus de voiture
                self.top_position = None
                self.bottom_position = None
            return vehicle_id
    
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
            vehicle_id = self.list_vehicles[self.bottom_position]
            self.list_vehicles[self.bottom_position] = None
            self.bottom_position -= 1
            if self.bottom_position < self.top_position: #si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ca veut dire qu'il n'y a plus de voiture
                self.bottom_position = None
                self.top_position = None
            return vehicle_id

    def is_top_available(self):
        return self.top_access and (self.top_position == None or self.top_position != 0)

    def is_bottom_available(self):
        return self.bottom_access and (self.top_position == None or self.bottom_position != self.length - 1)


    def push(self, id_vehicle, coté):
        if coté == "top":
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

        elif coté == "bottom":
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


    def pop(self, coté):
        if coté == "top":
            if self.top_position != None:
                vehicle_id = self.list_vehicles[self.top_position]
                self.list_vehicles[self.top_position] = None
                self.top_position += 1
                if self.top_position > self.bottom_position: # si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ca veut dire qu'il n'y a plus de voiture
                    self.top_position = None
                    self.bottom_position = None
                return vehicle_id

        elif coté == "bottom":
            if self.bottom_position != None:
                vehicle_id = self.list_vehicles[self.bottom_position]
                self.list_vehicles[self.bottom_position] = None
                self.bottom_position -= 1
                if self.bottom_position < self.top_position: # si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ca veut dire qu'il n'y a plus de voiture
                    self.bottom_position = None
                    self.top_position = None
                return vehicle_id






    
