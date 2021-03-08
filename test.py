from parking import *
from simulation import *

class TestTest() :
    def test_parking_init(self) :
        #assert Parking(Block(...)) == ...
        pass

    def test_push_lane(self):
        vehicle_1 = Vehicle(1,2,3,4)
        vehicle_2 = Vehicle(12,22,32,42)
        block = Block(3,5)
        lane = Lane(1, block, 10, 2, 5)

