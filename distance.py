import parking

def distance_manhattan(parking, place1, place2):   #: [Block, Lane, side]
    speed_max = 2  #m/s
    


class Parking():
    def __init__(self, blocks, disposal=[[]]):
        self.blocks = blocks
        self.occupation = dict()
        self.disposal = disposal
        #self.access = access
        self.nb_of_places = sum([block.height*block.width for block in self.blocks])
        L = []
        for block in self.blocks:
            L.append(len(block.lanes))
        nb_max_lanes = max(L)
        self.matrice_distances = np.empty((len(self.blocks), nb_max_lanes, 2, len(self.blocks), nb_max_lanes, 2))  #tenseur d'ordre 6 representant toutes les possibilités de Block-lane-top/bottom
        