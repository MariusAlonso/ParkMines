from parking import *
from simulation import *

class TestTest() :
    def test_parking_init(self) :
        #assert Parking(Block(...)) == ...
        pass

    def test_push_top(self):
        vehicle_1 = Vehicle(1,1,2,3,4)
        lane = Lane(0, 10)
        lane.push_top(vehicle_1.id) 
        assert lane.list_vehicles[5] == vehicle_1.id

    def test_push_top_2(self):
        vehicle_1 = Vehicle(1,1,2,3,4)
        vehicle_2 = Vehicle(2,12,22,32,42)
        lane = Lane(0, 10)
        lane.push_top(vehicle_1.id) 
        lane.push_top(vehicle_2.id) 
        assert lane.list_vehicles[4] == vehicle_2.id


