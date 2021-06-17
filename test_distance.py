import distance as dist
from parking import *

class TestTest():

    def test_search_pw_place(self):
        parking = Parking([BlockInterface([Lane(0, 1), Lane(1, 1), Lane(2, 1)]), Block([], 15, 10), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        distance = dist.Distance(parking)
        place1 = [0, 1, 0]
        place2 = [1, 3, 0]
        place3 = [1, 3, 1]
        assert distance.search_pw_place(place1) == [1, 0]  
        assert distance.search_pw_place(place2) == [4, 3]
        assert distance.search_pw_place(place3) == [4, 23]

    def test_distance_manhattan(self):
        parking = Parking([BlockInterface([Lane(0, 1), Lane(1, 1), Lane(2, 1)]), Block([], 15, 10), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        distance = dist.Distance(parking)
        place1 = [0, 1, 0]
        place2 = [1, 3, 0]
        place3 = [1, 3, 1]
        assert distance.distance_manhattan(place1, place2) == 6
        assert distance.distance_manhattan(place3, place2) == 20

    def test_fill_matrix(self):
        parking = Parking([Block([Lane(0, 1)]), Block([Lane(0, 1)])],  [[0,0,0,0], ["s",1,1,1]])
        distance = dist.Distance(parking)
        distance.fill_matrix_time()
        result = np.zeros((len(parking.blocks), parking.nb_max_lanes, 2, len(parking.blocks), parking.nb_max_lanes, 2))
        result[0][0][0][0][0][0] = 0.
        result[0][0][1][0][0][1] = 0.
        result[0][0][0][0][0][1] = 2.4
        result[0][0][1][0][0][0] = 2.4
        result[1][0][0][1][0][0] = 0.
        result[1][0][1][1][0][1] = 0.
        result[1][0][0][1][0][1] = 2.4
        result[1][0][1][1][0][0] = 2.4
        result[0][0][0][1][0][0] = 4*1.2
        result[0][0][1][1][0][1] = 4*1.2
        result[0][0][0][1][0][1] = 6*1.2
        result[0][0][1][1][0][0] = 2*1.2
        result[1][0][0][0][0][0] = 4*1.2
        result[1][0][1][0][0][1] = 4*1.2
        result[1][0][0][0][0][1] = 2*1.2
        result[1][0][1][0][0][0] = 6*1.2
        print(datetime.timedelta(0, distance.matrix_time[1][0][1][0][0][1]))
        assert np.all(distance.matrix_time == result)



