from display import *
from inputs import *
from parking import *

class TestTest():

    def test_display_parking(self):
        
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:70])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        display = Display(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom, 30, 40)

        assert 0 == 0

test = TestTest()
test.test_display_parking()