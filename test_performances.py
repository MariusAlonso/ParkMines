from parking import *
from simulation import *
from inputs import *
from performances import *

class TestTest():

    def testPositiveAverageMovesNumberDashboard(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, 1, parking, AlgorithmRandom)
        
        # test
        dashboard = Dashboard(simulation)
        averageMoves = "{:.1f}".format(dashboard.averageIntermediateMovesPerVehicle())
        # print(f"chaque véhicule effectue en moyenne {averageMoves} déplacements intermédaires")
        assert 0 <= dashboard.averageIntermediateMovesPerVehicle()
    
    def testPositiveAverageMovesNumberPerformance(self):
        # création du parking
        Vehicle.next_id = 1
        stock = Stock(importFromFile()[:13])
        parking = Parking([Block([Lane(1, 10), Lane(2, 10), Lane(3, 10), Lane(4, 10)])])
        
        # test
        performance = Performance(datetime.datetime(2016,1,1,0,0,0,0), stock, 1, parking, AlgorithmRandom)
        averageMoves = "{:.1f}".format(performance.averageDashboard())
        print(f"chaque véhicule effectue en moyenne {averageMoves} déplacements intermédaires")
        assert 0 <= performance.averageDashboard()