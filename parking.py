from simulation import Vehicle

class Parking() :
    def __init__(self, blocks):
        self.blocks = blocks


class Block() :
    def __init__(self, lanes):
        self.lanes = lanes


class Lane() :
    def __init__(self, id_lane, block, length, top_position, bottom_position, top_access = True, bottom_access = True) :
        self.length = length
        self.id = id_lane
        self.block = block
        self.length = length
        self.top_position = top_position
        self.bottom_position = bottom_position
        self.top_access = top_access
        self.bottom_access = bottom_access
        self.dict_vehicle = dict()                           # (id_vehicle : [id_vehicle_top, id_vehicle_bottom])
        self.top_id_vehicle = None
        self.bottom_id_vehicle = None

    def push_top(self, id_vehicle): 
        if not self.dict_vehicle:
            self.dict_vehicle[id_vehicle] = [None, None]
            self.top_id_vehicle = id_vehicle
            self.bottom_id_vehicle = id_vehicle
        else:
            self.dict_vehicle[self.top_id_vehicle][0] = id_vehicle   #on ajoute le nouveau véhicule au top de l'ancien top véhicule
            self.dict_vehicle[id_vehicle] = [None, self.top_id_vehicle]
            self.top_id_vehicle = id_vehicle

