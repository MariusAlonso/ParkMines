from parking import *
from simulation import *
from inputs import *
from performances import *
from robot import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class TestTest():



    ### Tests Dashboard ###


    
    def testPositiveAverageMovesNumberDashboard(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([BlockInterface([Lane(1, 1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        # averageMoves = "{:.1f}".format(dashboard.averageIntermediateMovesPerVehicle())
        # print(f"chaque véhicule effectue en moyenne {averageMoves} déplacements intermédaires")
        assert 0 <= dashboard.averageIntermediateMovesPerVehicle()

    def testAverageRetrievalDelay0(self):
        # création du parking
        y2015 = datetime.datetime(2015, 1, 1, 0, 0, 0, 0)
        y2017 = datetime.datetime(2017, 1, 1, 0, 0, 0, 0)
        y2018 = datetime.datetime(2018, 1, 1, 0, 0, 0, 0)
        y2019 = datetime.datetime(2019, 1, 1, 0, 0, 0, 0)
        stock = Stock([Vehicle(y2015, y2017, y2015, y2015), Vehicle(y2015, y2018, y2015, y2015), Vehicle(y2015, y2019, y2015, y2015)])
        parking = Parking([BlockInterface([Lane(1, 1),Lane(2, 1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules sont sortis avec un retard moyen de {dashboard.averageRetrievalDelay()}")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageRetrievalDelay()

    def testAverageBeforeDepositDelay0(self):
        # création du parking
        Vehicle.next_id = 1
        y2015 = datetime.datetime(2015, 1, 1, 0, 0, 0, 0)
        y2017 = datetime.datetime(2017, 1, 1, 0, 0, 0, 0)
        y2018 = datetime.datetime(2018, 1, 1, 0, 0, 0, 0)
        y2019 = datetime.datetime(2019, 1, 1, 0, 0, 0, 0)
        stock = Stock([Vehicle(y2015, y2017, y2015, y2015), Vehicle(y2015, y2018, y2015, y2015), Vehicle(y2015, y2019, y2015, y2015)])
        parking = Parking([BlockInterface([Lane(1, 1),Lane(2, 1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les clients attendent en moyenne {dashboard.averageBeforeDepositDelay()} heures avant de déposer leur véhicule")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageBeforeDepositDelay()

    def testAverageAfterDepositDelay0(self):
        # création du parking
        y2015 = datetime.datetime(2015, 1, 1, 0, 0, 0, 0)
        y2017 = datetime.datetime(2017, 1, 1, 0, 0, 0, 0)
        y2018 = datetime.datetime(2018, 1, 1, 0, 0, 0, 0)
        y2019 = datetime.datetime(2019, 1, 1, 0, 0, 0, 0)
        stock = Stock([Vehicle(y2015, y2017, y2015, y2015), Vehicle(y2015, y2018, y2015, y2015), Vehicle(y2015, y2019, y2015, y2015)])
        parking = Parking([BlockInterface([Lane(1, 1),Lane(2, 1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules restent en moyenne {dashboard.averageAfterDepositDelay()} heures dans l'interface")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageAfterDepositDelay()

    def testAverageRetrievalDelay1(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([BlockInterface([Lane(1, 1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules sont sortis avec un retard moyen de {dashboard.averageRetrievalDelay()}")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageRetrievalDelay()

    def testAverageBeforeDepositDelay1(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([BlockInterface([Lane(1, 1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les clients attendent en moyenne {dashboard.averageBeforeDepositDelay()} heures avant de déposer leur véhicule")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageBeforeDepositDelay()

    def testAverageAfterDepositDelay1(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([BlockInterface([Lane(1, 1)]),Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules restent en moyenne {dashboard.averageAfterDepositDelay()} heures dans l'interface")
        assert datetime.timedelta() <= dashboard.averageAfterDepositDelay()

    def testAverageRetrievalDelay2(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:70])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules sont sortis avec un retard moyen de {dashboard.averageRetrievalDelay()}")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageRetrievalDelay()

    def testAverageBeforeDepositDelay2(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:70])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les clients attendent en moyenne {dashboard.averageBeforeDepositDelay()} heures avant de déposer leur véhicule")
        assert datetime.timedelta() <= dashboard.averageBeforeDepositDelay()

    def testAverageAfterDepositDelay2(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:70])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules restent en moyenne {dashboard.averageAfterDepositDelay()} heures dans l'interface")
        assert datetime.timedelta() <= dashboard.averageAfterDepositDelay()
    
    def testAverageRetrievalDelay3(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:100])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules sont sortis avec un retard moyen de {dashboard.averageRetrievalDelay()}")
        assert datetime.timedelta() <= dashboard.averageRetrievalDelay()

    def testAverageBeforeDepositDelay3(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:100])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les clients attendent en moyenne {dashboard.averageBeforeDepositDelay()} heures avant de déposer leur véhicule")
        assert datetime.timedelta() <= dashboard.averageBeforeDepositDelay()

    def testAverageAfterDepositDelay3(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:70])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules restent en moyenne {dashboard.averageAfterDepositDelay()} heures dans l'interface")
        assert datetime.timedelta() <= dashboard.averageAfterDepositDelay()
    
    def testDepositDelaysRates(self, delays=[1, 5, 60], nb_vehicles=70, nb_repetition=10):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:nb_vehicles])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        delays_rates = dashboard.depositDelaysRates(delays)
        
        # affichage

        delays = np.zeros(len(delays_rates))
        ratios = np.zeros(len(delays_rates))
        i = 0

        for delay, ratio in delays_rates.items():
            delays[i] = delay
            ratios[i] = ratio
            i += 1

        plt.figure()
        plt.plot(delays, ratios)
        plt.show()


        assert 0 == 0



    ### Tests Performance ###



    def testAverageDashboard(self, stock_args=(5, ), nb_repetition=100, delays=[i for i in range(300)], display=False):
        # création du parking
        Vehicle.next_id = 1
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        performance = Performance(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock_args, [Robot(1)], parking, AlgorithmRandom, delays=delays)

        # test
        if display:
            performance.printAverageDashboard(nb_repetition)
        else:
            performance.averageDashboard(nb_repetition)
        assert 0 == 0
    
    def testVariableStockAndRobots(self, stock_args=(5, ), nb_repetition=10, delays=[i for i in range(300)], display=False):
        # création du parking
        Vehicle.next_id = 1
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        performance = Performance(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock_args, [Robot(1)], parking, AlgorithmUnimodal, delays=delays)

        # test
        performance.variableStockAndRobots(nb_repetition)
        assert 0 == 0
    
    def testVariableInterfaceAndRobots(self, stock_args=(5, ), nb_repetition=10, delays=[i for i in range(300)], display=False):
        # création du parking
        Vehicle.next_id = 1
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0, 0, 0, 0],["s", 1, 1, 1],[2,2,3,"e"]])
        performance = Performance(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock_args, [Robot(1)], parking, AlgorithmRandom, delays=delays)

        # test
        performance.variableInterfaceAndRobots(nb_repetition)
        assert 0 == 0

    def testVariableStockAndRobotsRealParking(self, stock_args=(5, ), nb_repetition=10, delays=[i for i in range(300)], display=False):
        # création du parking
        Vehicle.next_id = 1
        real_parking = Parking([BlockInterface([],10,1), Block([], 15, 7,"leftrigth"), Block([], 14, 7,"leftrigth"), Block([], 13, 6,"leftrigth"), Block([], 8, 7,"leftrigth"), Block([], 18, 7,"leftrigth"), Block([], 10, 11), Block([], 15, 1, "leftrigth")], [['s','s', 'f0:6', 'f0:6', 'e', 4, 6], [7,1,1,2,'f0:3', 4,6], [7,1,1,2,3,'f0:2', 6], [7,1,1,2,3,5,6], [7,'e','e','e',3,5,6], [7,'e','e','e','e',5,6], [7,'f7:0',0,0,0,5,6]])
        performance = Performance(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock_args, [Robot(1)], real_parking, AlgorithmRandom, delays=delays)

        # test
        performance.variableStockAndRobots(nb_repetition)
        assert 0 == 0

    def testVariableAlgorithmsAndRobotsRealParking(self, stock_args=(30, ), nb_repetition=10, delays=[i for i in range(300)], display=False):
        # création du parking
        Vehicle.next_id = 1
        real_parking = Parking([BlockInterface([],10,1), Block([], 15, 7,"leftrigth"), Block([], 14, 7,"leftrigth"), Block([], 13, 6,"leftrigth"), Block([], 8, 7,"leftrigth"), Block([], 18, 7,"leftrigth"), Block([], 10, 11), Block([], 15, 1, "leftrigth")], [['s','s', 'f0:6', 'f0:6', 'e', 4, 6], [7,1,1,2,'f0:3', 4,6], [7,1,1,2,3,'f0:2', 6], [7,1,1,2,3,5,6], [7,'e','e','e',3,5,6], [7,'e','e','e','e',5,6], [7,'f7:0',0,0,0,5,6]])
        performance = Performance(datetime.datetime(2016, 1, 1, 0, 0, 0, 0), stock_args, [Robot(1), Robot(2), Robot(3)], real_parking, AlgorithmRandom, delays=delays)

        # test
        performance.variableAlgorithmsAndRobots(nb_repetition)
        assert 0 == 0


# exécution hors pytest

test = TestTest()

#test.testAverageDashboard(stock_args=(5, ), display=True)
#test.testVariableStockAndRobots(nb_repetition=10)
#test.testVariableInterfaceAndRobots(nb_repetition=10)
#test.testVariableStockAndRobotsRealParking(stock_args=(30, ), nb_repetition=10)

test.testVariableAlgorithmsAndRobotsRealParking(nb_repetition=20)