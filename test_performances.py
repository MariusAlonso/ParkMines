from parking import *
from simulation import *
from inputs import *
from performances import *
from robot import *

class TestTest():
    
    def testPositiveAverageMovesNumberDashboard(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([BlockInterface([Lane(1,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        averageMoves = "{:.1f}".format(dashboard.averageIntermediateMovesPerVehicle())
        # print(f"chaque véhicule effectue en moyenne {averageMoves} déplacements intermédaires")
        assert 0 <= dashboard.averageIntermediateMovesPerVehicle()

    def testAverageRetrievalDelay0(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([BlockInterface([Lane(1,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules sont sortis avec un retard moyen de {dashboard.averageRetrievalDelay()}")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageRetrievalDelay()

    def testAverageBeforeDepositDelay0(self):
        # création du parking
        Vehicle.next_id = 1
        y2015 = datetime.datetime(2015,1,1,0,0,0,0)
        y2017 = datetime.datetime(2017,1,1,0,0,0,0)
        y2018 = datetime.datetime(2018,1,1,0,0,0,0)
        y2019 = datetime.datetime(2019,1,1,0,0,0,0)
        stock = Stock([Vehicle(y2015, y2017, y2015, y2015), Vehicle(y2015, y2018, y2015, y2015), Vehicle(y2015, y2019, y2015, y2015)])
        parking = Parking([BlockInterface([Lane(1,1),Lane(2,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les clients attendent en moyenne {dashboard.averageBeforeDepositDelay()} heures avant de déposer leur véhicule")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageBeforeDepositDelay()

    def testAverageAfterDepositDelay0(self):
        # création du parking
        y2015 = datetime.datetime(2015,1,1,0,0,0,0)
        y2017 = datetime.datetime(2017,1,1,0,0,0,0)
        y2018 = datetime.datetime(2018,1,1,0,0,0,0)
        y2019 = datetime.datetime(2019,1,1,0,0,0,0)
        stock = Stock([Vehicle(y2015, y2017, y2015, y2015), Vehicle(y2015, y2018, y2015, y2015), Vehicle(y2015, y2019, y2015, y2015)])
        parking = Parking([BlockInterface([Lane(1,1),Lane(2,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules restent en moyenne {dashboard.averageAfterDepositDelay()} heures dans l'interface")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageAfterDepositDelay()

    def testAverageRetrievalDelay1(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([BlockInterface([Lane(1,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules sont sortis avec un retard moyen de {dashboard.averageRetrievalDelay()}")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageRetrievalDelay()

    def testAverageBeforeDepositDelay1(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([BlockInterface([Lane(1,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les clients attendent en moyenne {dashboard.averageBeforeDepositDelay()} heures avant de déposer leur véhicule")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageBeforeDepositDelay()

    def testAverageAfterDepositDelay1(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([BlockInterface([Lane(1,1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules restent en moyenne {dashboard.averageAfterDepositDelay()} heures dans l'interface")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageAfterDepositDelay()


test = TestTest()

test.testAverageRetrievalDelay0()
test.testAverageBeforeDepositDelay0()
test.testAverageAfterDepositDelay0()

print("---NEW CONFIG---")

test.testAverageRetrievalDelay1()
test.testAverageBeforeDepositDelay1()
test.testAverageAfterDepositDelay1()