from parking_2 import *
from simulation import *

class TestTest() :
    def test_parking_init(self) :
        #assert Parking(Block(...)) == ...
        pass

    def test_push_lane(self):
        vehicle_1 = Vehicle(1,1,2,3,4)
        vehicle_2 = Vehicle(2,12,22,32,42)
        block = Block(5)
        lane = Lane(1, block, 10, 2, 5)
        lane.push_top(vehicle_1.id) 
        assert lane.dict_vehicle == {vehicle_1.id: [None, None]}

    def test_push_lane_2(self):
        vehicle_1 = Vehicle(1,1,2,3,4)
        vehicle_2 = Vehicle(2,12,22,32,42)
        block = Block(5)
        lane = Lane(1, block, 10, 2, 5)
        lane.push_top(vehicle_1.id) 
        lane.push_top(vehicle_2.id)
        assert lane.dict_vehicle == {vehicle_1.id: [vehicle_2.id, None], vehicle_2.id: [None, vehicle_1.id]}
