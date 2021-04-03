from parking import *
from simulation import *
from inputs import *
from vehicle import RandomStock
import datetime
from copy import deepcopy

class Dashboard():

    def __init__(self, simulation):
        """
        un Dashboard prend en argument une simulation, l'exécute entièrement,
        puis calcule la performance
        """
        self.completed = True
        try:
            simulation.complete()
        except:
            self.completed = False
        self.simulation = simulation

    def averageIntermediateMovesPerVehicle(self):
        if len(self.simulation.stock):
            return self.simulation.algorithm.nb_placements/len(self.simulation.stock) - 1
        else:
            return 0
    
    def averageBeforeDepositDelay(self):
        before_deposit_delays = np.array(self.simulation.before_deposit_delays)
        if len(before_deposit_delays[before_deposit_delays < datetime.timedelta()]):
            before_deposit_delays[before_deposit_delays < datetime.timedelta()] = datetime.timedelta()
        if len(before_deposit_delays):
            return np.mean(before_deposit_delays)
        else:
            return datetime.timedelta()

    def averageAfterDepositDelay(self):
        after_deposit_delays = np.array(self.simulation.after_deposit_delays)
        if len(after_deposit_delays[after_deposit_delays < datetime.timedelta()]):
            after_deposit_delays[after_deposit_delays < datetime.timedelta()] = datetime.timedelta()
        if len(after_deposit_delays):
            return np.mean(after_deposit_delays)
        else:
            return datetime.timedelta()
    
    def averageRetrievalDelay(self):
        retrieval_delays = np.array(self.simulation.retrieval_delays)
        if len(retrieval_delays[retrieval_delays < datetime.timedelta()]):
            retrieval_delays[retrieval_delays < datetime.timedelta()] = datetime.timedelta()
        if len(retrieval_delays):
            return np.mean(retrieval_delays)
        else:
            return datetime.timedelta()
    
    def depositDelaysRates(self, delays=[1, 5, 60]):
        """
        renvoie un dictionnaire donnant pour chaque durée dt dans delays, la part des clients ayant attendu plus de dt minutes
        """
        deposit_delays = np.array(self.simulation.before_deposit_delays)
        delays_rates = {}

        for delay in delays:
            delays_rates[delay] = np.mean(deposit_delays > datetime.timedelta(minutes=delay))
        
        return delays_rates
    
    def retrievalDelaysRates(self, delays=[1, 5, 60]):
        """
        renvoie un dictionnaire donnant pour chaque durée dt dans delays, la part des clients ayant attendu plus de dt minutes
        """
        retrieval_delays = np.array(self.simulation.retrieval_delays)
        delays_rates = {}

        for delay in delays:
            delays_rates[delay] = np.mean(retrieval_delays > datetime.timedelta(minutes=delay))
        
        return delays_rates



class Performance():

    def __init__(self, t0, stock_args, robots, parking, AlgorithmType, delays=[1, 5, 60]):
        """
        Dans la classe performance, on se donne une simulation de référence
        et on se donne des méthodes qui étudient la réponse à la variation 
        d'un seul des paramètres (par rapport à la simulation de référence)

        stock_args : tuple contenant tous les arguments nécessaires à la génération du stock
        ( on veut pouvoir faire stock = Stock(*stock_args) )
        """
        self.stock_args = stock_args
        self.robots = robots
        # t0 la date d'initial
        self.t = t0
        self.parking = parking
        self.algorithm = AlgorithmType
        self.delays = delays
    
    def averageDashboard(self, nb_repetition=10, congestion_coeff=1.):
        """
        renvoie les données du Dashboard de la simulation de référence,
        moyennées sur nb_repetition répétitions
        """
        average_dashboard = {}
        effective_nb_repetition = 0
        average_intermediate_mpv = 0.
        average_before_deposit_delay = datetime.timedelta()
        average_after_deposit_delay = datetime.timedelta()
        average_retrieval_delay = datetime.timedelta()
        average_deposit_delay_rates = {key: 0. for key in self.delays}
        average_retrieval_delay_rates = {key: 0. for key in self.delays}

        for _ in range(nb_repetition):
            simulation = Simulation(self.t, RandomStock(*self.stock_args), deepcopy(self.robots), deepcopy(self.parking), deepcopy(self.algorithm))
            dashboard = Dashboard(simulation)
            if dashboard.completed and dashboard.simulation.retrieval_delays:
                average_intermediate_mpv += dashboard.averageIntermediateMovesPerVehicle()
                #print("average_before_deposit_delay", average_before_deposit_delay)
                #print("dashboard.averageBeforeDepositDelay()", dashboard.averageBeforeDepositDelay())
                average_before_deposit_delay += dashboard.averageBeforeDepositDelay()
                #print("average_after_deposit_delay", average_after_deposit_delay)
                #print("dashboard.averageAfterDepositDelay()", dashboard.averageAfterDepositDelay())
                average_after_deposit_delay += dashboard.averageAfterDepositDelay()
                #print("average_retrieval_delay", average_retrieval_delay)
                #print("dashboard.averageRetrievalDelay()", dashboard.averageRetrievalDelay())
                average_retrieval_delay += dashboard.averageRetrievalDelay()

                deposit_delay_rates = dashboard.depositDelaysRates(self.delays)
                for delay in deposit_delay_rates:
                    average_deposit_delay_rates[delay] += deposit_delay_rates[delay]
                
                retrieval_delay_rates = dashboard.retrievalDelaysRates(self.delays)
                for delay in retrieval_delay_rates:
                    average_retrieval_delay_rates[delay] += retrieval_delay_rates[delay]

                effective_nb_repetition += 1
        
        for key, value in average_deposit_delay_rates.items():
            average_deposit_delay_rates[key] = value / effective_nb_repetition
        
        for key, value in average_retrieval_delay_rates.items():
            average_retrieval_delay_rates[key] = value / effective_nb_repetition

        average_dashboard["average_intermediate_mpv"] = average_intermediate_mpv / effective_nb_repetition
        average_dashboard["average_before_deposit_delay"] = average_before_deposit_delay / effective_nb_repetition
        average_dashboard["average_after_deposit_delay"] = average_after_deposit_delay / effective_nb_repetition
        average_dashboard["average_retrieval_delay"] = average_retrieval_delay / effective_nb_repetition
        average_dashboard["average_deposit_delay_rates"] = average_deposit_delay_rates # attention, c'est un dictionnaire
        average_dashboard["average_retrieval_delay_rates"] = average_retrieval_delay_rates # attention, c'est un dictionnaire
        print(f"{effective_nb_repetition}/{nb_repetition} simulations réussies")

        return average_dashboard

    def variableStock(self, list_congestion_coeffs, nb_repetition=10):
        """
        regarde l'influence d'une variation du stock sur les différents retards, en moyennant sur nb_repetition répétitions
        """
        list_dashboards = []
        for congestion_coeff in list_congestion_coeffs:
            list_dashboards.append(self.averageDashboard(nb_repetition, congestion_coeff))
        
        return list_dashboards