

class Parking() :
    def __init__(self, blocks):
        self.blocks = blocks


class Block() :
    def __init__(self, nb_lanes, lane_length):
        self.lanes = []
        for _ in range(nb_lanes) :
            self.lanes.append(Lane(lane_length))


class Lane() :
    def __init__(self, length) :
        self.length = length