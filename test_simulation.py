from parking import *
from simulation import *
from inputs import *
from robot import *

class TestTest():
    def test_stock_simulation_init(self):
        Vehicle.next_id = 1
        stock = Stock([Vehicle(3, 4, 1, 3), Vehicle(2, 1, 0, 3), Vehicle(3, 6, 2, 4)])
        parking = Parking([BlockInterface([Lane(1,1),Lane(1,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(0, stock, [Robot(1)], parking, AlgorithmRandom)
        assert simulation.events[0].vehicle.id == 2
    """
    def test_random(self):
        Vehicle.next_id = 1
        stock = Stock([Vehicle(-1, 1, -1, -1), Vehicle(-1, 2, -1, -1), Vehicle(-1, 3, -1, -1)])
        parking = Parking([BlockInterface([Lane(1,1),Lane(1,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(0, stock, [Robot(1)], parking, AlgorithmRandom, print_in_terminal=True)
        assert 2 in simulation.parking.occupation
        block_id, lane_id, position = simulation.parking.occupation[2]
        assert simulation.parking.blocks[block_id].lanes[lane_id].list_vehicles[position] == 2
    """
    def test_inputs_random(self):
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:5])
        parking = Parking([BlockInterface([Lane(1,1),Lane(1,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom, print_in_terminal=True)
        simulation.next_event(3)
        #assert 10 in simulation.parking.blocks[0].lanes[0].list_vehicles or 10 in simulation.parking.blocks[0].lanes[1].list_vehicles
        simulation.complete()
        assert 1 not in simulation.parking.blocks[0].lanes[0].list_vehicles or 1 in simulation.parking.blocks[0].lanes[1].list_vehicles

test = TestTest()
test.test_inputs_random()
