from parking import *
from simulation import *

class TestTest() :
    def test_stock_simulation_init(self) :
        stock = Stock([Vehicle(1, 0, 0, 1, 3), Vehicle(2, 0, 0, 0, 3), Vehicle(3, 0, 0, 2, 4)])
        parking = Parking([Block([Lane(1, None, 10, 10, 10), Lane(2, None, 10, 10, 10)])])
        assert stock.order_events[0].vehicle.id is 2

    def test_random(self) :
        stock = Stock([Vehicle(1, 0, 1, -1, -1), Vehicle(2, 0, 2, -1, -1), Vehicle(3, 0, 3, -1, -1)])
        parking = Parking([Block([Lane(1, None, 10, 10, 10), Lane(2, None, 10, 10, 10)])])
        simulation = Simulation(0, stock, 1, parking)
        simulation.next_event()
        assert 1 in simulation.parking.blocks[0].lanes[0].dict_vehicle or 1 in simulation.parking.blocks[0].lanes[1].dict_vehicle