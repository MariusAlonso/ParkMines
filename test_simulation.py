from parking import *
from simulation import *

class TestTest():
    def test_stock_simulation_init(self):
        stock = Stock([Vehicle(0, 0, 1, 3), Vehicle(0, 0, 0, 3), Vehicle(0, 0, 2, 4)])
        parking = Parking([Block([Lane(1, 10), Lane(2, 10)])])
        assert stock.order_events[0].vehicle.id is 2

    def test_random(self):
        Vehicle.next_id = 1
        stock = Stock([Vehicle(-1, 1, -1, -1), Vehicle(-1, 2, -1, -1), Vehicle(-1, 3, -1, -1)])
        parking = Parking([Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(0, stock, 1, parking)
        simulation.next_event()
        assert 1 in simulation.parking.blocks[0].lanes[0].list_vehicles or 1 in simulation.parking.blocks[0].lanes[1].list_vehicles
        assert 2 in simulation.parking.occupation