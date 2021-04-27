from vehicle import *

class TestTest():

    def test_test(self):
        assert 0 == 0

    def test_duration_simu(self):
        stock = RandomStock()
        first_day, last_day = stock.duration_simu()
        print(first_day, last_day)
        assert last_day - first_day > datetime.timedelta()
    
test = TestTest()
test.test_duration_simu()