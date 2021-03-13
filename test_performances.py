from parking import *
from simulation import *
from inputs import *
from performances import *

class TestTest():

    def testPositiveAverageMovesNumber(self):
        Vehicle.next_id = 1
        stock = Stock(import_from_file()[:15])
        parking = Parking([Block([Lane(1, 10), Lane(2, 10)])])
        simulation = Simulation(datetime.datetime(2016,1,1,0,0,0,0), stock, 1, parking, AlgorithmRandom)
        dashboard = Dashboard(simulation)
        print(f"{len(simulation.stock)} véhicules")
        print(f"{simulation.algorithm.nb_placements} placements")
        print(f"chaque véhicule effectue en moyenne {dashboard.averageIntermediateMovesPerVehicle()} déplacements intermédaires")
        assert 0 <= dashboard.averageIntermediateMovesPerVehicle()