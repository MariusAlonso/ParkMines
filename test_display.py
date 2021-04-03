from display import *
from inputs import *
from parking import *
from vehicle import *
import sys

class TestTest():

    def test_display_parking(self):
        
        Vehicle.next_id = 1
        stock = RandomStock(10)
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 15, 10), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        with open("log.txt", "w") as log_file:
            sys.stdout = log_file
            display = Display(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1), Robot(2)], parking, AlgorithmRandom, 30, 40, print_in_terminal = True)

        assert 0 == 0

test = TestTest()
test.test_display_parking()