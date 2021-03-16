from parking import *
from simulation import *

class TestTest() :
    def test_parking_init(self) :
        #assert Parking(Block(...)) == ...
        pass

    def test_push_top(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        lane = Lane(0, 10)
        lane.push_top(vehicle_1.id) 
        assert lane.list_vehicles[5] == vehicle_1.id

    def test_push_top_2(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        vehicle_2 = Vehicle(12,22,32,42)
        lane = Lane(0, 10)
        lane.push_top(vehicle_1.id) 
        lane.push_top(vehicle_2.id) 
        assert lane.list_vehicles[4] == vehicle_2.id

    def test_push_bottom(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        lane = Lane(0, 10)
        lane.push_bottom(vehicle_1.id) 
        assert lane.list_vehicles[5] == vehicle_1.id

    def test_push_bottom_2(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        vehicle_2 = Vehicle(12,22,32,42)
        lane = Lane(0, 10)
        lane.push_bottom(vehicle_1.id) 
        lane.push_bottom(vehicle_2.id) 
        assert lane.list_vehicles[6] == vehicle_2.id

    def test_pop_top(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        vehicle_2 = Vehicle(12,22,32,42)
        lane = Lane(0, 10)
        lane.push_top(vehicle_1.id) 
        lane.push_top(vehicle_2.id)
        lane.pop_top()
        assert lane.list_vehicles[4] == None
        assert lane.top_position == 5
        lane.pop_top()
        assert lane.list_vehicles[5] == None
        assert lane.top_position == None

    def test_pop_bottom(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        vehicle_2 = Vehicle(12,22,32,42)
        lane = Lane(0, 10)
        lane.push_bottom(vehicle_1.id) 
        lane.push_bottom(vehicle_2.id)
        lane.pop_bottom()
        assert lane.list_vehicles[6] == None
        assert lane.bottom_position == 5
        lane.pop_bottom()
        assert lane.list_vehicles[5] == None
        assert lane.bottom_position == None

    def test_is_top_available(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        vehicle_2 = Vehicle(12,22,32,42)
        lane = Lane(0, 2)
        lane.push_top(vehicle_1.id) 
        assert lane.is_top_available() == True
        assert lane.top_position == 1
        lane.push_top(vehicle_2)
        assert lane.is_top_available() == False
        assert lane.top_position == 0

    def test_is_bottom_available(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        vehicle_2 = Vehicle(12,22,32,42)
        lane = Lane(0, 2)
        assert lane.is_bottom_available() == True
        lane.push_bottom(vehicle_1.id)
        assert lane.is_bottom_available() == False
        assert lane.bottom_position == 1
      
    def test_repr_lane(self):
        lane = Lane(0, 2)
        print(lane)

    def test_push(self):
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, bottom) 
        assert lane.list_vehicles[5] == vehicle_1.id
        Vehicle.next_id = 1
        vehicle_1 = Vehicle(1,2,3,4)
        lane = Lane(0, 10)
        lane.push(vehicle_1.id, top) 
        assert lane.list_vehicles[5] == vehicle_1.id





    
    


