from simulation import Vehicle
import numpy as np

class Parking() :
    def __init__(self, blocks):
        self.blocks = blocks


class Block() :
    def __init__(self, lanes):
        self.lanes = lanes

class Lane() :
    def __init__(self, id_lane, length, top_access = True, bottom_access = True):
        self.length = length
        self.id = id_lane
        self.list_vehicles = np.empty(self.length)
        self.length = length
        self.top_position = None
        self.bottom_position = None
        self.top_access = top_access
        self.bottom_access = bottom_access
        self.top_id_vehicle = None
        self.bottom_id_vehicle = None

    def push_top(self, id_vehicle):
        if self.top_position == None:
            if not self.bottom_access:
                self.list_vehicles[self.length - 1] = id_vehicle
                self.top_position = self.length - 1
                self.bottom_position = self.length -1
            else:
                self.list_vehicles[self.length//2] = id_vehicle
                self.top_position = self.length//2
                self.bottom_position = self.length//2
        else:
            self.list_vehicles[self.top_position-1] = id_vehicle
            self.top_position -= 1


       

    
