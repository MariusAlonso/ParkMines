from simulation import *
from inputs import *
from parking import *
from vehicle import *
import sys

class TestTest():

    def test_display_parking(self):
        
        Vehicle.next_id = 1
        stock = RandomStock(5, time = datetime.timedelta(days=1000))
        print(len(stock.vehicles))
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 15, 10), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        real_parking2 = Parking([BlockInterface([],10,1,"leftrigth"), Block([], 15, 7), Block([], 14, 7), Block([], 13, 6), Block([], 8, 7), Block([], 18, 7), Block([], 10, 11,"leftrigth")], [['s', 'f7:0',1,1,1],['s', 'f3:0',1,1,1], ['s','f3:0',0,2,2], ['s','f3:0',3,3,3], ['s',5,5,4,4], ['s','f3:0',6,6,6]])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 10, 10, "leftrigth"), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,"f3:0", 3]])
        real_parking = Parking([BlockInterface([],10,1), Block([], 15, 7,"leftrigth"), Block([], 14, 7,"leftrigth"), Block([], 13, 6,"leftrigth"), Block([], 8, 7,"leftrigth"), Block([], 18, 7,"leftrigth"), Block([], 10, 11), Block([], 15, 1, "leftrigth")], [['s','s', 'f0:6', 'f0:6', 'e', 4, 6], [7,1,1,2,'f0:3', 4,6], [7,1,1,2,3,'f0:2', 6], [7,1,1,2,3,5,6], [7,'e','e','e',3,5,6], [7,'e','e','e','e',5,6], [7,'f7:0',0,0,0,5,6]])
        with open("log.txt", "w") as log_file:
            sys.stdout = log_file
            simulation = Simulation(datetime.datetime(2000,1,1,0,0,0,0), stock, [Robot(1), Robot(2)], parking, AlgorithmUnimodal, print_in_terminal = False)
            simulation.start_display(12, 20)
            simulation.display.run()
            print(simulation.display)

        assert 0 == 0

test = TestTest()
test.test_display_parking()