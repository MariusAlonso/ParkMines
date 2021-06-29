from simulation import Vehicle
import numpy as np
import datetime
import distance as dist
from copy import copy, deepcopy

class Parking():
    def __init__(self, blocks, disposal=[[]], occupation={}):

        self.real_parking = [BlockInterface([],10,1), Block([], 15, 7,"leftrigth"), Block([], 14, 7,"leftrigth"), Block([], 13, 6,"leftrigth"), Block([], 8, 7,"leftrigth"), Block([], 18, 7,"leftrigth"), Block([], 10, 11), Block([], 15, 1, "leftrigth")], [['s','s', 'f0:6', 'f0:6', 'e', 4, 6], [7,1,1,2,'f0:3', 4,6], [7,1,1,2,3,'f0:2', 6], [7,1,1,2,3,5,6], [7,'e','e','e',3,5,6], [7,'e','e','e','e',5,6], [7,'f7:0',0,0,0,5,6]]

        ### Attributs variant au cours d'une simulation

        self.occupation = occupation
        self.blocks = blocks
        self.number_blocks = len(blocks)

        ### Attributs ne variant pas au cours d'une simulation

        self.place_ratio = 2                # ratio longueur/largeur des places pour l'affichage

        self.nb_of_places = sum([block.height*block.width for block in self.blocks])
        L = []
        for block in self.blocks:
            L.append(len(block.lanes))
        self.nb_max_lanes = max(L)          # block contenant le plus de lane

        L = []
        for block in self.blocks:
            L.append(len(block.lanes[0].list_vehicles))
        self.longest_lane = max(L)          # lane la plus longue du parking

        ### Calcul des coordonnées du maillage correspondant à la matrice disposal
        
        # disposal est une matrice permettant de placer les blocks l'un par rapport à l'autre
        # - s => espace vide, de la largeur d'une place
        # - e => espace vide, dont les dimensions ne sont pas imposées
        # - f4:5 => espace vide, de largeur 4 et de hauteur 5
        self.disposal = disposal
        max_i_disposal = len(self.disposal)
        max_j_disposal = len(self.disposal[0])
        self.x_in_pw = [0]*max_j_disposal
        self.y_in_pw = [0]*max_i_disposal

        for i_disposal in range(1, max_i_disposal):   

            for j_disposal in range(max_j_disposal):

                block_id = self.disposal[i_disposal][j_disposal]

                if self.disposal[i_disposal-1][j_disposal] != block_id:
                    k = i_disposal - 1
                    while k >=0 and self.disposal[k][j_disposal] == self.disposal[i_disposal-1][j_disposal]:
                        k -= 1

                    block_id = self.disposal[k+1][j_disposal]
                    if type(block_id) == str or self.blocks[block_id].direction == "topbottom":
                        self.y_in_pw[i_disposal] = max(self.y_in_pw[i_disposal], self.y_in_pw[k+1] + self.block_height(block_id))
                    else:
                        self.y_in_pw[i_disposal] = max(self.y_in_pw[i_disposal], self.y_in_pw[k+1] + self.block_width(block_id))

        for j_disposal in range(1, max_j_disposal):   

            for i_disposal in range(max_i_disposal):

                block_id = self.disposal[i_disposal][j_disposal]

                if self.disposal[i_disposal][j_disposal-1] != block_id:
                    k = j_disposal - 1
                    while k >=0 and self.disposal[i_disposal][k] == self.disposal[i_disposal][j_disposal-1]:
                        k -= 1

                    block_id = self.disposal[i_disposal][k+1]
                    if type(block_id) == str or self.blocks[block_id].direction == "topbottom":
                        self.x_in_pw[j_disposal] = max(self.x_in_pw[j_disposal], self.x_in_pw[k+1] + self.block_width(block_id))
                    else:
                        self.x_in_pw[j_disposal] = max(self.x_in_pw[j_disposal], self.x_in_pw[k+1] + self.block_height(block_id))

        ### Calcul de la matrice des distances
        
        distance = dist.Distance(self)
        distance.fill_matrix_time()
        self.matrix_time = distance.matrix_time

        ### Calcul des dictionnaires de correspondance entre les indices globaux de lane et les indices (block_id, lane_id)

        self.dict_lanes = dict()
        self.to_global_id = dict()
        self.number_lanes = 0
        counter_lanes = 1                              # LA NUMEROTAION DES LANES COMMENCE A 1
        for block_id, block in enumerate(self.blocks):
            self.number_lanes += block.nb_lanes
            for lane_id, lane in enumerate(block.lanes):
                self.dict_lanes[counter_lanes] = (block_id, lane_id)
                self.to_global_id[(block_id, lane_id)] = counter_lanes
                counter_lanes += 1
         

    
    def _copy(self):
        """
        Crée une copie profonde d'un parking en conservant son état d'occupation
        """
        parking_copied = copy(self)
        parking_copied.blocks = [block._copy() for block in self.blocks]
        parking_copied.occupation = self.occupation.copy()
        return parking_copied
    
    def _empty_copy(self):
        """
        Crée une copie profonde d'un parking en réinitialisant son état d'occupation
        """
        parking_copied = copy(self)
        parking_copied.blocks = [block._empty_copy() for block in self.blocks]
        parking_copied.occupation = self.occupation.copy()
        return parking_copied               
    
    def __repr__(self):
        s = ""
        for block in self.blocks[1:]:
            s += "\n" + block.__repr__()
        
        return " - Interface :\n"+self.blocks[0].__repr__()+"\n - Parking :"+s
    
    def travel_time(self, departure, arrival):
        """
        Renvoie le temps de trajet entre l'extrémité departure et l'extrémité arrival

        departure : (block_id, lane_id, side)
        arrival : (block_id, lane_id, side)
        """
        if departure == arrival:
            return datetime.timedelta(0,30, minutes=1)
        else:
            if departure[2] == 'top':
                place1 = (departure[0], departure[1], 0)
            else:
                place1 = (departure[0], departure[1], 1)
            if arrival[2] == 'top':
                place2 = (arrival[0], arrival[1], 0)
            else:
                place2 = (arrival[0], arrival[1], 1)
            duree = self.matrix_time[place1[0]][place1[1]][place1[2]][place2[0]][place2[1]][place2[2]]
        return datetime.timedelta(0,int(duree)) + datetime.timedelta(0,30, minutes=1)
    
    def block_width(self, block_id):
        if block_id == "s":
            return 1
        if block_id == "l":
            return 9
        elif block_id == "e":
            return 0
        elif type(block_id) == str and block_id[0] == "f":
            return int(block_id[1:].split(":")[0])
        return len(self.blocks[block_id].lanes)+1

    def block_height(self, block_id):
        if block_id == "s":
            return 1
        if block_id == "l":
            return 7
        elif block_id == "e":
            return 0
        elif type(block_id) == str and block_id[0] == "f":
            return int(block_id[1:].split(":")[1])
        return self.blocks[block_id].lanes[0].length*self.place_ratio + 1
    
    def opposite(self, side):
        if side == "top":
            return "bottom"
        if side == "bottom":
            return "top"

    def future_config(self, lane, block_id, lane_id, robots, stock, min_time = None, max_time = None, on_place=False):

        if on_place:
            lane_copy = lane
        else:
            lane_copy = deepcopy(lane)

        for robot in robots:
            if not robot.doing is None:
                if (not max_time or robot.goal_time and robot.goal_time <= max_time):
                    if (not min_time or robot.goal_time and robot.goal_time > min_time):
                        if robot.goal_position[0:2] == (block_id, lane_id):
                            side = robot.goal_position[2]
                            if robot.vehicle is None:
                                lane_copy.pop(side)
                            else:
                                lane_copy.push(robot.vehicle.id, side, stock)
        
        return lane_copy
    
    def reverse_config(self, block_id, lane_id, events_to_reverse, stock):

        input("ATTENTION\nParking.reverse_config NON FONCTIONNEL")

        lane = self.blocks[block_id].lanes[lane_id]

        for event in events_to_reverse[::-1]:
            if len(event) == 1:
                lane.pop(event[0])
            else:
                lane.push(event[1], event[0], stock)
                 


class Block():
    def __init__(self, lanes, nb_lanes=None, lane_length=None, direction="topbottom"):

        if nb_lanes:
            self.lanes = []
            for i in range(1, nb_lanes+1):
                self.lanes.append(Lane(i, lane_length))
            self.nb_lanes = nb_lanes
            self.lane_length = lane_length
        else:
            self.lanes = lanes
            self.nb_lanes = len(self.lanes)
            self.lane_length = self.lanes[0].length

        # dimensions
        self.height = len(self.lanes) # en nombre de voitures
        self.width = self.lanes[0].length # en nombre de voitures

        self.x_pos = None
        self.y_pos = None

        self.direction = direction

    def _copy(self):
        block_copied = copy(self)
        block_copied.lanes = [deepcopy(lane) for lane in self.lanes]
        if isinstance(self, BlockInterface):
            block_copied.targeted = self.targeted[:]    # message d'erreur car l'attribut n'existe que pour l'interface
        return block_copied

    def _empty_copy(self):
        block_copied = copy(self)
        block_copied.lanes = [lane._empty_copy() for lane in self.lanes]
        if isinstance(self, BlockInterface):
            block_copied.nb_places_available = self.height
            block_copied.targeted = [False]*self.height
        return block_copied

    
    def __repr__(self):
        # on représente les lanes horizontalement pour construire et on transpose avant d'afficher
        
        matrix = np.empty((self.height, self.width), dtype='<U6')
        for row_index, lane in enumerate(self.lanes):
            liste = lane.list_vehicles[:]
            liste = [str(item).replace("0", '-') for item in liste]
            matrix[row_index] = liste

        # les lanes sont les colonnes (la première à gauche)
        # conformément aux termes top et bottom pour les extrémités
        return matrix.__repr__()


class BlockInterface(Block):

    def __init__(self, lanes, nb_lanes=None, lane_length=None, direction="topbottom"):
        super().__init__(lanes, nb_lanes, lane_length, direction)
        self.nb_places_available = self.height
        self.targeted = [False]*self.height

    def empty_lane(self): #renvoie "full" si interface est pleine, et return premier vehicule
        for i_lane, lane in enumerate(self.lanes):
            if lane.list_vehicles[0] == 0:
                return i_lane
        else:
            return "full"

    def occupied_lane(self): #renvoie "empty" si interface est pleine, et return premier vehicule
        for i_lane, lane in enumerate(self.lanes):
            if lane.list_vehicles[0] != 0:
                return i_lane
        else:
            return "empty"



class Lane() :
    def __init__(self, id_lane, length, top_access = True, bottom_access = True):
        self.length = length
        self.id = id_lane
        self.list_vehicles = [0]*self.length
        self.top_position = None                # indice de la premiere voiture occupée dans la lane (None si pas de voiture)
        self.bottom_position = None             # indice de la derniere voiture occupée dans la lane (None si pas de voiture)
        self.future_top_position = None  
        self.future_bottom_position = None      
        self.top_access = top_access
        self.bottom_access = bottom_access
        self.argmax_retrieval = None
    
    def _empty_copy(self):
        return Lane(self.id, self.length, self.top_access, self.bottom_access)

    def __repr__(self):
        liste = self.list_vehicles[:]
        liste = [str(item).replace('0', '-') for item in liste]
        return liste.__repr__()

    def is_top_available(self):
        m = 1 # Maxint
        if not self.future_top_position is None:
            m = self.future_top_position
        if not self.top_position is None:
            m = min(m, self.top_position)
        return self.top_access and m > 0

    def is_bottom_available(self):
        M = -1 # Minint
        if not self.future_bottom_position is None:
            M = self.future_bottom_position
        if not self.bottom_position is None:
            M = max(M, self.bottom_position)   
        return self.bottom_access and M < self.length - 1
    
    def is_end_available(self, side):
        if side == "top":
            return self.is_top_available()
        if side == "bottom":
            return self.is_bottom_available()

    def end_position(self, side):
        if side == "top":
            return self.top_position
        if side == "bottom":
            return self.bottom_position
    
    def end_limit(self, side):
        if side == "top":
            return 0
        if side == "bottom":
            return self.length - 1

    def future_end_position(self, side):
        if side == "top":
            return self.future_top_position
        if side == "bottom":
            return self.future_bottom_position


    def push(self, id_vehicle, side, stock):
        if side == "top":
            if self.top_position == None:
                if not self.bottom_access:
                    self.list_vehicles[-1] = id_vehicle
                    self.top_position = self.length - 1
                    self.bottom_position = self.length -1
                else:
                    self.list_vehicles[self.length//2] = id_vehicle
                    self.top_position = self.length//2
                    self.bottom_position = self.length//2
                
                self.argmax_retrieval = self.top_position
            else:
                self.list_vehicles[self.top_position-1] = id_vehicle
                max_retrieval = stock.vehicles[self.list_vehicles[self.argmax_retrieval]].retrieval
                if self.argmax_retrieval == self.top_position and stock.vehicles[id_vehicle].retrieval > max_retrieval:
                    self.argmax_retrieval -= 1
                self.top_position -= 1

        elif side == "bottom":
            if self.bottom_position == None:
                if not self.top_access:
                    self.list_vehicles[0] = id_vehicle
                    self.top_position = 0
                    self.bottom_position = 0
                else:
                    self.list_vehicles[self.length//2] = id_vehicle
                    self.top_position = self.length//2
                    self.bottom_position = self.length//2
                
                self.argmax_retrieval = self.top_position
            else:
                self.list_vehicles[self.bottom_position + 1] = id_vehicle
                max_retrieval = stock.vehicles[self.list_vehicles[self.argmax_retrieval]].retrieval
                if self.argmax_retrieval == self.bottom_position and stock.vehicles[id_vehicle].retrieval > max_retrieval:
                    self.argmax_retrieval += 1
                self.bottom_position += 1

    def push_reserve(self, id_vehicle, side, mark=True):
        if side == "top":
            if self.future_top_position == None:
                if not self.bottom_access:
                    self.future_top_position = self.length - 1
                    self.future_bottom_position = self.length -1
                else:
                    self.future_top_position = self.length//2
                    self.future_bottom_position = self.length//2
            else:
                self.future_top_position -= 1

        elif side == "bottom":
            if self.future_bottom_position == None:
                if not self.top_access:
                    self.future_top_position = 0
                    self.future_bottom_position = 0
                else:
                    self.future_top_position = self.length//2
                    self.future_bottom_position = self.length//2
            else:
                self.future_bottom_position += 1

    def push_cancel_reserve(self, side):
        if side == "top":
            if self.future_top_position != None:
                self.future_top_position += 1
                if self.future_top_position > self.future_bottom_position: # si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ça veut dire qu'il n'y a plus de voiture
                    self.future_top_position = None
                    self.future_bottom_position = None

        elif side == "bottom":
            if self.future_bottom_position != None:
                self.future_bottom_position -= 1
                if self.future_top_position > self.future_bottom_position: # si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ça veut dire qu'il n'y a plus de voiture
                    self.future_top_position = None
                    self.future_bottom_position = None


    def pop_reserve(self, side):
        self.push_cancel_reserve(side)


    def pop_cancel_reserve(self, side):
        self.push_reserve(0, side)

    def pop(self, side):
        if side == "top":
            if self.top_position != None:
                vehicle_id = self.list_vehicles[self.top_position]
                self.list_vehicles[self.top_position] = 0
                self.top_position += 1
                if self.top_position > self.bottom_position: # si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ça veut dire qu'il n'y a plus de voiture
                    self.top_position = None
                    self.bottom_position = None
                    self.argmax_retrieval = None
                elif self.top_position > self.argmax_retrieval:
                    self.argmax_retrieval = self.top_position
                return vehicle_id

        elif side == "bottom":
            if self.bottom_position != None:
                vehicle_id = self.list_vehicles[self.bottom_position]
                self.list_vehicles[self.bottom_position] = 0
                self.bottom_position -= 1
                if self.bottom_position < self.top_position: # si jamais l'indice de la premiere voiture est plus grand que celui de la dernière, ça veut dire qu'il n'y a plus de voiture
                    self.bottom_position = None
                    self.top_position = None
                    self.argmax_retrieval = None
                elif self.bottom_position < self.argmax_retrieval:
                    self.argmax_retrieval = self.bottom_position
                return vehicle_id


    def retrieval_side(self, position, stock):
        """
        renvoie le côté de sortie (a priori) du véhicule situé en position position, None si il n'y en a pas
        """
        vehicle = stock.vehicles[self.list_vehicles[position]]
        # on vérifie qu'il y a bien un véhicule à cette place
        if vehicle:
            bottom_displacement = 0
            top_displacement = 0
            # on parcours toutes les positions pour voir si le véhicule gène
            for i in range(self.length):
                # on vérifie qu'il y a bien un véhicule en place i
                if self.list_vehicles[i]:
                    vehicle_i = stock.vehicles[self.list_vehicles[i]]
                    # on regarde si il va falloir le déplacer
                    if vehicle_i.retrieval > vehicle.retrieval:
                        # il faudra déplacer ce véhicule, on regarde si il est côté top ou côté bottom
                        if i < position:
                            top_displacement += 1 
                        else:
                            bottom_displacement += 1
            # on renvoie le côté pour lequel le nombre de véhicules à déplacer est le plus petit
            if top_displacement <= bottom_displacement:
                return "top"
            else:
                return "bottom"
        else:
            return None

    
    def next_retrieval(self, side, stock, exception=None):
        """
        renvoie la date de prochaine sortie d'un véhicule par ce coté de la lane
        on suppose qu'un véhicule sort par le côté où il y a le moins de véhicule à déplacer
        Attention : peut renvoyer None si la lane est vide
        """
        retrieval = None

        for position, vehicle_id in enumerate(self.list_vehicles):
            # on vérifie que le véhicule n'est pas None et qu'il va bien sortir par notre côté
            if vehicle_id and self.retrieval_side(position, stock) == side:
                vehicle = stock.vehicles[vehicle_id]
                # on diminue la date de prochaine sortie de ce côté si besoin
                if retrieval is None or retrieval > vehicle.retrieval:
                    if not vehicle.retrieval == exception:
                        retrieval = vehicle.retrieval
        
        return retrieval



    
