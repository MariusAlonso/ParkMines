from parking import *


class Distance():
    def __init__(self, parking):
        self.parking = parking
        self.time_per_pw = 1.2 #secondes pour parcourir une pw a vitesse croisière
        
        self.matrix_time = np.zeros((len(self.parking.blocks), self.parking.nb_max_lanes, 2, len(self.parking.blocks), self.parking.nb_max_lanes, 2))  #tenseur d'ordre 6 representant toutes les possibilités de Block-lane-top/bottom
                                                                                                                            #top=0, bottom=1
    def __repr__(self):
        return self.parking

    def search_pw_place(self, place1):     #achtung! l'id des lanes commence a 0
        index1 = []
        ratio = self.parking.place_ratio
        for id_line, line in enumerate(self.parking.disposal):
            for id_block, block in enumerate(line):
                if (block == place1[0]) and (not index1):
                    index1 = [self.parking.x_in_pw[id_block] + place1[1], self.parking.y_in_pw[id_line] + place1[2]*ratio*self.parking.blocks[place1[0]].width]
        return index1

    def distance_manhattan(self, place1, place2):   #: [Block, Lane, side: 0 pour top, 1 pour bottom]
        speed_max = 2  #m/s
        index1 = self.search_pw_place(place1)
        index2 = self.search_pw_place(place2)
        return abs(index1[0] - index2[0]) + abs(index1[1] - index2[1])

    def time_manhattan(self, place1, place2):
        return self.time_per_pw*self.distance_manhattan(place1, place2)

    def fill_matrix_time(self):
        matrix = self.matrix_time
        for id_block1, block1 in enumerate(self.parking.blocks):
            for id_block2, block2 in enumerate(self.parking.blocks):
                for id_lane1, lane1 in enumerate(block1.lanes):
                    for id_lane2, lane2 in enumerate(block2.lanes):
                        if lane1.top_access:
                            if lane2.top_access:
                                place1 = [id_block1, id_lane1, 0]
                                place2 = [id_block2, id_lane2, 0]
                                matrix[id_block1][id_lane1][0][id_block2][id_lane2][0] = self.time_manhattan(place1, place2)
                            if lane2.bottom_access:
                                place1 = [id_block1, id_lane1, 0]
                                place2 = [id_block2, id_lane2, 1]
                                matrix[id_block1][id_lane1][0][id_block2][id_lane2][1] = self.time_manhattan(place1, place2)
                        if lane1.bottom_access:
                            if lane2.top_access:
                                place1 = [id_block1, id_lane1, 1]
                                place2 = [id_block2, id_lane2, 0]
                                matrix[id_block1][id_lane1][1][id_block2][id_lane2][0] = self.time_manhattan(place1, place2)
                            if lane2.bottom_access:
                                place1 = [id_block1, id_lane1, 1]
                                place2 = [id_block2, id_lane2, 1]
                                matrix[id_block1][id_lane1][1][id_block2][id_lane2][1] = self.time_manhattan(place1, place2)



        


 

                



