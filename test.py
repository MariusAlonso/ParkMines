from parking import *
from simulation import *

class TestTest() :
    def test_parking_init(self) :
        #assert Parking(Block(...)) == ...
        pass

    def test_push_top():
        vehicle_1 = Vehicle(1,1,2,3,4)
        lane = Lane(0, 10)
        lane.push_top(vehicle_1.id) 
        assert lane.list_vehicles == []


