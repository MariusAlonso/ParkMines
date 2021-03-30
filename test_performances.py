from parking import *
from simulation import *
from inputs import *
from performances import *
from robot import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
        y2015 = datetime.datetime(2015,1,1,0,0,0,0)
        y2017 = datetime.datetime(2017,1,1,0,0,0,0)
        y2018 = datetime.datetime(2018,1,1,0,0,0,0)
        y2019 = datetime.datetime(2019,1,1,0,0,0,0)
        stock = Stock([Vehicle(y2015, y2017, y2015, y2015), Vehicle(y2015, y2018, y2015, y2015), Vehicle(y2015, y2019, y2015, y2015)])
        parking = Parking([BlockInterface([Lane(1,1),Lane(2,1)]),Block([Lane(1, 10), Lane(2, 10)])])
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

    def testAverageRetrievalDelay2(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:70])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules sont sortis avec un retard moyen de {dashboard.averageRetrievalDelay()}")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageRetrievalDelay()

    def testAverageBeforeDepositDelay2(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:70])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les clients attendent en moyenne {dashboard.averageBeforeDepositDelay()} heures avant de déposer leur véhicule")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageBeforeDepositDelay()

    def testAverageAfterDepositDelay2(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:70])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules restent en moyenne {dashboard.averageAfterDepositDelay()} heures dans l'interface")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageAfterDepositDelay()
    
    def testAverageRetrievalDelay3(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:100])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules sont sortis avec un retard moyen de {dashboard.averageRetrievalDelay()}")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageRetrievalDelay()

    def testAverageBeforeDepositDelay3(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:100])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les clients attendent en moyenne {dashboard.averageBeforeDepositDelay()} heures avant de déposer leur véhicule")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageBeforeDepositDelay()

    def testAverageAfterDepositDelay3(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:100])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        print(f"les véhicules restent en moyenne {dashboard.averageAfterDepositDelay()} heures dans l'interface")
        assert datetime.timedelta(0, 0, 0, 0, 0, 0) <= dashboard.averageAfterDepositDelay()
    
    def testAverageDashboard(self,nb_vehicles=70, nb_repetition=10):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:nb_vehicles])
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        performance = Performance(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)

        # test
        means = performance.averageDashboard(nb_repetition)
        for key in means:
            print(key, means[key])
        
        assert 0 == 0

    def testVariableStock(self, nb_repetition=10):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile())
        parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10), Lane(5, 10), Lane(6, 10), Lane(7, 10), Lane(8, 10)]), Block([Lane(1, 4), Lane(2, 4)]), Block([Lane(1, 2)])], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        performance = Performance(datetime.datetime(2016,1,1,0,0,0,0), stock, [Robot(1)], parking, AlgorithmRandom)

        # test
        list_congestion_coeffs = [0.05, 0.1, 0.15, 0.2, 0.3]
        list_means = performance.variableStock(list_congestion_coeffs, nb_repetition=nb_repetition)




        for key in list_means[0]:
            time_list = [means[key] for means in list_means]
            print(key, time_list)

            f = plt.figure()
            ax = f.add_subplot(1,1,1)
            ax.set_title(key)

            if key == "average_intermediate_mpv":
                ax.scatter(list_congestion_coeffs, time_list)
            else:
                # specify a date to use for the times
                zero = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
                time = [zero + t for t in time_list]

                ax.scatter(list_congestion_coeffs, time)
        
            plt.show()
        
        assert 0 == 0




# exécution hors pytest

test = TestTest()
"""
print("\n" + "simulation écarts annuels" + "\n")

test.testAverageBeforeDepositDelay0()
test.testAverageAfterDepositDelay0()
test.testAverageRetrievalDelay0()

print("\n" + "simulation 13 véhicules, 2 lanes" + "\n")

test.testAverageBeforeDepositDelay1()
test.testAverageAfterDepositDelay1()
test.testAverageRetrievalDelay1()

print("\n" + "simulation complète 70 véhicules" + "\n")

test.testAverageBeforeDepositDelay2()
test.testAverageAfterDepositDelay2()
test.testAverageRetrievalDelay2()

print("\n" + "simulation complète 100 véhicules" + "\n")

test.testAverageBeforeDepositDelay3()
test.testAverageAfterDepositDelay3()
test.testAverageRetrievalDelay3()

print("\n" + "test dashboard moyen" + "\n")
"""
test.testVariableStock(1)