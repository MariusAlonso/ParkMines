from parking import *
from simulation import *
from inputs import *

class TestTest():
    def test_stock_simulation_init(self):
        Vehicle.next_id = 1
        stock = Stock([Vehicle(3, 4, 1, 3), Vehicle(2, 1, 0, 3), Vehicle(3, 6, 2, 4)])
        parking = Parking([Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(0, stock, 1, parking)
        assert simulation.events[0].vehicle.id is 2

    def test_random(self):
        Vehicle.next_id = 1
        stock = Stock([Vehicle(-1, 1, -1, -1), Vehicle(-1, 2, -1, -1), Vehicle(-1, 3, -1, -1)])
        parking = Parking([Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(0, stock, 1, parking)
        simulation.next_event()
        assert 1 in simulation.parking.blocks[0].lanes[0].list_vehicles or 1 in simulation.parking.blocks[0].lanes[1].list_vehicles
        assert 2 in simulation.parking.occupation

    def test_inputs_random(self):
        Vehicle.next_id = 1
        stock = Stock(import_from_file()[:9])
        parking = Parking([Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2020,1,1,0,0,0,0), stock, 1, parking)
        simulation.next_event()
        assert 1 in simulation.parking.blocks[0].lanes[0].list_vehicles or 1 in simulation.parking.blocks[0].lanes[1].list_vehicles