from parking import *
from simulation import *

class TestTest():

    def test_parking_init(self) :
        # assert Parking(Block(...)) == ...
        pass

    def test_push_top(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, "top") 
        assert lane.list_vehicles[5] == vehicle_1.id

    def test_push_top_2(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        vehicle_2 = Vehicle(12, 22, 32, 42)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, "top") 
        lane.push(vehicle_2.id, "top") 
        assert lane.list_vehicles[4] == vehicle_2.id

    def test_push_bottom(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, "bottom") 
        assert lane.list_vehicles[5] == vehicle_1.id

    def test_push_bottom_2(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        vehicle_2 = Vehicle(12, 22, 32, 42)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, "bottom") 
        lane.push(vehicle_2.id, "bottom") 
        assert lane.list_vehicles[6] == vehicle_2.id

    def test_pop_top(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        vehicle_2 = Vehicle(12, 22, 32, 42)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, "top") 
        lane.push(vehicle_2.id, "top")
        lane.pop("top")
        assert lane.list_vehicles[4] == None
        assert lane.top_position == 5
        lane.pop("top")
        assert lane.list_vehicles[5] == None
        assert lane.top_position == None

    def test_pop_bottom(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        vehicle_2 = Vehicle(12, 22, 32, 42)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, "bottom") 
        lane.push(vehicle_2.id, "bottom")
        lane.pop("bottom")
        assert lane.list_vehicles[6] == None
        assert lane.bottom_position == 5
        lane.pop("bottom")
        assert lane.list_vehicles[5] == None
        assert lane.bottom_position == None

    def test_is_top_available(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        vehicle_2 = Vehicle(12, 22, 32, 42)
        lane = Lane(0, 2)
        lane.push(vehicle_1.id, "top") 
        assert lane.is_top_available() == True
        assert lane.top_position == 1
        lane.push(vehicle_2.id, "top")
        assert lane.is_top_available() == False
        assert lane.top_position == 0

    def test_is_bottom_available(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        vehicle_2 = Vehicle(12, 22, 32, 42)
        lane = Lane(0, 2)
        assert lane.is_bottom_available() == True
        lane.push(vehicle_1.id, "bottom")
        assert lane.is_bottom_available() == False
        assert lane.bottom_position == 1
      
    def test_repr_lane(self):
        lane = Lane(0, 2)
        print(lane)

    def test_push(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, "bottom") 
        assert lane.list_vehicles[5] == vehicle_1.id
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, "top") 
        assert lane.list_vehicles[5] == vehicle_1.id
    
    def testNumberOfPlaces(self):
        parking = Parking([Block([Lane(1, 10), Lane(2, 10)]), Block([Lane(1, 7), Lane(2, 7)])])
        assert parking.nb_of_places == 34

    def testCopy(self):
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 15, 10, "leftright"), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        parking_copied = parking._copy()
        assert parking_copied.x_in_pw is parking.x_in_pw
        assert not parking_copied.blocks is parking.blocks

    def testEmptyCopy(self):
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 15, 10, "leftright"), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1, 2, 3, 4)
        parking.blocks[0].lanes[0].push(vehicle_1.id, "top")
        parking_copied = parking._empty_copy()
        assert 1 in parking.blocks[0].lanes[0].list_vehicles
        assert 1 not in parking_copied.blocks[0].lanes[0].list_vehicles

test = TestTest()
test.testCopy()
test.testEmptyCopy()




    
    


