import parking
import display

def distance_manhattan(parking, place1, place2):   #: [Block, Lane, side]
    speed_max = 2  #m/s
    


class Distance():
    def __init__(self, parking, display):
        self.blocks = parking.blocks
        self.disposal = parking.disposal
        self.place_length = display.place_length
        self.place_width = display.place_width
        self.x0 = display.x0
        self.y0 = display.y0
        L = []
        for block in self.blocks:
            L.append(len(block.lanes))
        nb_max_lanes = max(L)
        self.matrice_distances = np.empty((len(self.blocks), nb_max_lanes, 2, len(self.blocks), nb_max_lanes, 2))  #tenseur d'ordre 6 representant toutes les possibilités de Block-lane-top/bottom
        

    def search_place_in_disposal(self, place1, place2):
        index1 = []
        index2 = []
        for line in self.disposal:
            count_lane_of_1 = 0
            index_first_block_1 = None
            count_lane_of_2 = 0
            index_first_block_2 = None
            for block in line:
                if block == place1[0] and (not index1):
                    count_lane_of_1 += self.x0[block]
                    if place1[1] <= count_lane_of_1:
                        index1 = [line, block] 
                elif block == place2[0] and (not index2):
                    count_lane_of_2 += self.x0[block]
                    if place2[1] <= count_lane_of_2:
                        index2 = [line, block] 
        return index1, index2
                



