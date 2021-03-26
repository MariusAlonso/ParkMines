from parking import *
from simulation import *
from inputs import *
import datetime

class Dashboard():

    def __init__(self, simulation):
        """
        un Dashboard prend en argument une simulation, l'exécute entièrement,
        puis calcule la performance
        """
        simulation.complete()
        self.simulation = simulation

    def averageIntermediateMovesPerVehicle(self):
        if len(self.simulation.stock):
            return self.simulation.algorithm.nb_placements/len(self.simulation.stock) - 1
        else:
            return 0
    
    def averageRetrievalDelay(self):
        retrieval_delays = np.array(self.simulation.retrieval_delays)
        retrieval_delays[retrieval_delays < datetime.timedelta(0, 0, 0, 0, 0, 0)] = 0.
        return np.mean(retrieval_delays)
    
    def averageBeforeDepositDelay(self):
        before_deposit_delays = np.array(self.simulation.before_deposit_delays)
        before_deposit_delays[before_deposit_delays < datetime.timedelta(0, 0, 0, 0, 0, 0)] = 0.
        return np.mean(before_deposit_delays)

    def averageAfterDepositDelay(self):
        after_deposit_delays = np.array(self.simulation.after_deposit_delays)
        after_deposit_delays[after_deposit_delays < datetime.timedelta(0, 0, 0, 0, 0, 0)] = 0.
        return np.mean(after_deposit_delays)



class Performance():

    def __init__(self, t0, stock, robots, parking, AlgorithmType):
        """
        Dans la classe performance, on se donne une simulation de référence
        et on se donne des méthodes qui étudient la réponse à la variation 
        d'un seul des paramètres (par rapport à la simulation de référence)
        """
        self.stock = stock
        self.robots = robots
        # t0 la date d'initial
        self.t = t0
        self.parking = parking
        self.algorithm = AlgorithmType
    
    def averageDashboard(self, nb_repetition=100):
        """
        renvoie les données du Dashboard de la simulation de référence,
        moyennées sur nb_repetition répétitions
        """
        average = 0
        for _ in range(nb_repetition):
            simulation = Simulation(self.t, self.stock, self.robots, self.parking, self.algorithm)
            average += Dashboard(simulation).averageIntermediateMovesPerVehicle()

        average /= nb_repetition
        return average
    
    def variableStock(self, nb_repetition=100):
        pass