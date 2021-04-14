from display import *
from inputs import *
from parking import *
from vehicle import *
import sys

class TestTest():

    def test_display_parking(self):
        
        Vehicle.next_id = 1
        stock = RandomStock(30)
        print(len(stock.vehicles))
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 15, 10), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        real_parking = Parking([BlockInterface([],10,1), Block([], 15, 7), Block([], 14, 7), Block([], 13, 6), Block([], 8, 7), Block([], 18, 7), Block([], 10, 11)], [['s','f7:0',0,0,0], ['s', 'f7:0',1,1,1], ['s','f7:0',2,2,2], ['s','f7:0',3,3,'s'], ['s',5,5,5,4], ['s','f7:0',6,6,6]])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 15, 10, "leftrigth"), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,"f10:0", 3]])
        with open("log.txt", "w") as log_file:
            sys.stdout = log_file
            display = Display(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1), Robot(2), Robot(3), Robot(4)], real_parking, AlgorithmRandom, 14, 17, print_in_terminal = True)

        assert 0 == 0

test = TestTest()
test.test_display_parking()