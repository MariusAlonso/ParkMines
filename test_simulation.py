from parking import *
from simulation import *
from inputs import *
from robot import *
import numpy as np
import matplotlib.pyplot as plt

class TestTest():
    def test_stock_simulation_init(self):
        Vehicle.next_id = 1
        y2020 = datetime.datetime(2020,1,1,0,0,0,0)
        y2017 = datetime.datetime(2017,1,1,0,0,0,0)
        y2018 = datetime.datetime(2018,1,1,0,0,0,0)
        y2019 = datetime.datetime(2019,1,1,0,0,0,0)
        stock = Stock([Vehicle(y2019, y2020, y2018, y2018), Vehicle(y2020, y2018, y2017, y2019), Vehicle(y2020, y2020, y2019, y2020)])
        parking = Parking([BlockInterface([Lane(1,1),Lane(2,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        assert simulation.events[0].vehicle.id == 2
    
    def test_random(self):
        Vehicle.next_id = 1
        y2015 = datetime.datetime(2015,1,1,0,0,0,0)
        y2017 = datetime.datetime(2017,1,1,0,0,0,0)
        y2018 = datetime.datetime(2018,1,1,0,0,0,0)
        y2019 = datetime.datetime(2019,1,1,0,0,0,0)
        stock = Stock([Vehicle(y2015, y2017, y2015, y2015), Vehicle(y2015, y2018, y2015, y2015), Vehicle(y2015, y2019, y2015, y2015)])
        parking = Parking([BlockInterface([Lane(1,1),Lane(2,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom, print_in_terminal=True)
        assert 2 in simulation.parking.occupation
        block_id, lane_id, position = simulation.parking.occupation[2]
        assert simulation.parking.blocks[block_id].lanes[lane_id].list_vehicles[position] == 2
        simulation.complete()
    
    def test_inputs_random(self):
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:70])
        parking = Parking([BlockInterface([], 2, 1), Block([], 10, 10)])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom, print_in_terminal=False)
        simulation.complete()
        assert 1 not in simulation.parking.occupation
    
    def testNbEvents(self):
        # création du parking
        Vehicle.next_id = 1
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), RandomStock(*(5, )), [Robot(1)], parking, AlgorithmRandom, print_in_terminal=False)
        
        # test
        simulation.complete()

        dates = []
        lengths = []

        for date, length in simulation.nb_events_tracker.items():
            dates.append(date)
            lengths.append(length)
        
        dates = np.array(dates)
        lengths = np.array(lengths)

        plt.plot(dates, lengths)
        plt.xlabel("date")
        plt.ylabel("nombre d'évènements dans la pile")
        plt.title("évolution du nombre d'évènements dans la pile au cours du temps")
        plt.show()

test = TestTest()
test.testNbEvents()