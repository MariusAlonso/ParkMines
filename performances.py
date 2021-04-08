from parking import *
from simulation import *
from inputs import *
from vehicle import RandomStock
import datetime
from copy import deepcopy
from math import isclose
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
    
    def depositDelaysRates(self, delays=[i for i in range(300)]):
        """
        renvoie un dictionnaire donnant pour chaque durée dt dans delays, la part des clients ayant attendu plus de dt minutes
        """
        deposit_delays = np.array(self.simulation.before_deposit_delays)
        delays_rates = {}

        for delay in delays:
            delays_rates[delay] = np.mean(deposit_delays > datetime.timedelta(minutes=delay))
        
        return delays_rates
    
    def retrievalDelaysRates(self, delays=[i for i in range(180)]):
        """
        renvoie un dictionnaire donnant pour chaque durée dt dans delays, la part des clients ayant attendu plus de dt minutes
        """
        retrieval_delays = np.array(self.simulation.retrieval_delays)
        delays_rates = {}

        for delay in delays:
            delays_rates[delay] = np.mean(retrieval_delays > datetime.timedelta(minutes=delay))
        
        return delays_rates



class Performance():

    def __init__(self, t0, stock_args, robots, parking, AlgorithmType, delays=[i for i in range(180)]):
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
    
    def averageDashboard(self, nb_repetition=10):
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
                average_before_deposit_delay += dashboard.averageBeforeDepositDelay()
                average_after_deposit_delay += dashboard.averageAfterDepositDelay()
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
        average_dashboard["success_rate"] = effective_nb_repetition / nb_repetition
        average_dashboard["average_deposit_delay_rates"] = average_deposit_delay_rates # attention, c'est un dictionnaire
        average_dashboard["average_retrieval_delay_rates"] = average_retrieval_delay_rates # attention, c'est un dictionnaire

        return average_dashboard
    
    def printAverageDashboard(self, nb_repetition=10):
        """
        affiche les résulats de averageDashboard
        """
        means = self.averageDashboard(nb_repetition=nb_repetition)
        for key in means:

            if key == "average_deposit_delay_rates":

                average_deposit_delay_rates = means[key]

                delays = np.zeros(len(average_deposit_delay_rates))
                ratios = np.zeros(len(average_deposit_delay_rates))
                i = 0

                for delay, ratio in average_deposit_delay_rates.items():
                    delays[i] = delay
                    ratios[i] = ratio
                    i += 1

                plt.figure()
                plt.plot(delays, ratios)
                plt.xlabel("minorant du temps d'attente pour le dépôt")
                plt.ylabel("part des clients concernés")
                plt.title("average_deposit_delay_rates")
                plt.show()

            elif key == "average_retrieval_delay_rates":

                average_retrieval_delay_rates = means[key]

                delays = np.zeros(len(average_retrieval_delay_rates))
                ratios = np.zeros(len(average_retrieval_delay_rates))
                i = 0

                for delay, ratio in average_retrieval_delay_rates.items():
                    delays[i] = delay
                    ratios[i] = ratio
                    i += 1

                plt.figure()
                plt.plot(delays, ratios)
                plt.xlabel("minorant du temps d'attente pour la sortie")
                plt.ylabel("part des clients concernés")
                plt.title("average_retrieval_delay_rates")
                plt.show()

            else:
                print(key, means[key])

    def variableStockAndRobots(self, nb_repetition=10, factors=[1+0.05*i for i in range(-8, 5)], nb_robots_max=3):
        """
        regarde l'influence d'une variation du stock sur les différents retards, en moyennant sur nb_repetition répétitions
        """
        # curves = {(factor, nb_robots): dictionnaire des performances pour ce facteur et ce nombre de robots}
        curves = {}

        # remplissage du dictionnaire curves
        for factor in factors:
            stock_args = tuple(factor*np.array(self.stock_args))
            for nb_robots in range(1, nb_robots_max + 1):
                # génération de toutes les sorties
                performance = Performance(self.t, stock_args, [Robot(i) for i in range(1, nb_robots + 1)], deepcopy(self.parking), deepcopy(self.algorithm))
                curves[(factor, nb_robots)] = performance.averageDashboard(nb_repetition)

        # tracé
        ref_flow = self.stock_args[0]

        ### before deposit ###

        before_deposit = plt.subplot(3, 3, 1)
        # abscisses : le flow journalier moyen
        flow = []
        # ordonnées : liste (indexée par le nombre de robots) des listes de retards
        delay = [[] for i in range(nb_robots)]
        for factor, nb_robots in curves:
            if nb_robots == nb_robots_max:
                flow.append(factor*ref_flow)
            delay[nb_robots-1].append(curves[factor, nb_robots]['average_before_deposit_delay'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array([duration.total_seconds()/60.0 for duration in delay[nb_robots-1]])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot '
            else:
                label = str(nb_robots) + ' robots'
            before_deposit.plot(x, y, label=label)
        
        # titre et légende
        before_deposit.legend()
        before_deposit.set_xlabel("flux journalier moyen")
        before_deposit.set_ylabel("temps d'attente (min)")
        before_deposit.set_title("attente client avant dépôt")
        before_deposit.autoscale(tight=True)

        ### after deposit ###
        
        after_deposit = plt.subplot(3, 3, 2)
        # abscisses : le flow journalier moyen
        flow = []
        # ordonnées : liste (indexée par le nombre de robots) des listes de retards
        delay = [[] for i in range(nb_robots)]
        for factor, nb_robots in curves:
            if nb_robots == nb_robots_max:
                flow.append(factor*ref_flow)
            delay[nb_robots-1].append(curves[factor, nb_robots]['average_after_deposit_delay'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array([duration.total_seconds()/60.0 for duration in delay[nb_robots-1]])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot'
            else:
                label = str(nb_robots) + ' robots'
            after_deposit.plot(x, y, label=label)
        
        # titre et légende
        after_deposit.legend()
        after_deposit.set_xlabel("flux journalier moyen")
        after_deposit.set_ylabel("temps d'attente (min)")
        after_deposit.set_title("attente véhicule dans interface après dépôt")
        after_deposit.autoscale(tight=True)

        ### retrieval ###
        
        retrieval = plt.subplot(3, 3, 3)
        # abscisses : le flow journalier moyen
        flow = []
        # ordonnées : liste (indexée par le nombre de robots) des listes de retards
        delay = [[] for i in range(nb_robots)]
        for factor, nb_robots in curves:
            if nb_robots == nb_robots_max:
                flow.append(factor*ref_flow)
            delay[nb_robots-1].append(curves[factor, nb_robots]['average_retrieval_delay'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array([duration.total_seconds()/60.0 for duration in delay[nb_robots-1]])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot'
            else:
                label = str(nb_robots) + ' robots'
            retrieval.plot(x, y, label=label)
        
        # titre et légende
        retrieval.legend()
        retrieval.set_xlabel("flux journalier moyen")
        retrieval.set_ylabel("temps d'attente (min)")
        retrieval.set_title("attente client avant récupération")
        retrieval.autoscale(tight=True)

        ### average_intermediate_mpv ###
        
        average_intermediate_mpv = plt.subplot(3, 3, 4)
        # abscisses : le flow journalier moyen
        flow = []
        # ordonnées : liste (indexée par le nombre de robots) des nombres de mouvements
        moves = [[] for i in range(nb_robots)]
        for factor, nb_robots in curves:
            if nb_robots == nb_robots_max:
                flow.append(factor*ref_flow)
            moves[nb_robots-1].append(curves[factor, nb_robots]['average_intermediate_mpv'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array(moves[nb_robots-1])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot'
            else:
                label = str(nb_robots) + ' robots'
            average_intermediate_mpv.plot(x, y, label=label)
        
        # titre et légende
        average_intermediate_mpv.legend()
        average_intermediate_mpv.set_xlabel("flux journalier moyen")
        average_intermediate_mpv.set_ylabel("nombre de mouvements")
        average_intermediate_mpv.set_title("nombre de mouvements intermédiaires")
        average_intermediate_mpv.autoscale(tight=True)

        ### success_rate ###
        
        success_rate = plt.subplot(3, 3, 7)
        # abscisses : le flow journalier moyen
        flow = []
        # ordonnées : liste (indexée par le nombre de robots) des taux de succès
        rate = [[] for i in range(nb_robots)]
        for factor, nb_robots in curves:
            if nb_robots == nb_robots_max:
                flow.append(factor*ref_flow)
            rate[nb_robots-1].append(curves[factor, nb_robots]['success_rate'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array(rate[nb_robots-1])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot'
            else:
                label = str(nb_robots) + ' robots'
            success_rate.plot(x, y, label=label)
        
        # titre et légende
        success_rate.set_ylim([0., 1.1])
        success_rate.legend()
        success_rate.set_xlabel("flux journalier moyen")
        success_rate.set_ylabel("taux de succès")
        success_rate.set_title("taux de succès de l'algorithme")
        success_rate.autoscale(tight=True)

        ### average_deposit_delay_rates ###
        
        deposit_delays = plt.subplot(3, 3, (5, 8))
        
        for factor, nb_robots in curves:
            # abscisses : le retard
            delays = []
            # ordonnées : la part des clients concernés
            ratios = []
            # on trace les distributions pour tous les nombres de robots et pour les flux entiers (arbitraire)
            if isclose(factor*ref_flow, int(factor*ref_flow)):
                #on récupère la courbe pour ce flux et ce nombre de robots
                average_deposit_delay_rates = curves[factor, nb_robots]['average_deposit_delay_rates']
                # construction des tableaux à tracer
                for delay, ratio in average_deposit_delay_rates.items():
                    delays.append(delay)
                    ratios.append(ratio)
                
                # tracé
                x = np.array(delays)
                y = np.array(ratios)

                label = f"r={nb_robots}, f={int(factor*ref_flow)}"

                deposit_delays.plot(x, y, label=label)        
        
        # titre et légende
        deposit_delays.legend()
        deposit_delays.set_xlabel("minorant du temps d'attente pour la sortie (min)")
        deposit_delays.set_ylabel("part des clients concernés")
        deposit_delays.set_title("temps d'attente moyen au dépôt")
        deposit_delays.autoscale(tight=True)

        ### average_retrieval_delay_rates ###
        
        retrieval_delays = plt.subplot(3, 3, (6, 9))
        
        for factor, nb_robots in curves:
            # abscisses : le retard
            delays = []
            # ordonnées : la part des clients concernés
            ratios = []
            # on trace les distributions pour tous les nombres de robots et pour les flux entiers (arbitraire)
            if isclose(factor*ref_flow, int(factor*ref_flow)):
                #on récupère la courbe pour ce flux et ce nombre de robots
                average_retrieval_delay_rates = curves[factor, nb_robots]['average_retrieval_delay_rates']
                # construction des tableaux à tracer
                for delay, ratio in average_retrieval_delay_rates.items():
                    delays.append(delay)
                    ratios.append(ratio)
                
                # tracé
                x = np.array(delays)
                y = np.array(ratios)

                label = f"r={nb_robots}, f={int(factor*ref_flow)}"

                retrieval_delays.plot(x, y, label=label)        
        
        # titre et légende
        retrieval_delays.legend()
        retrieval_delays.set_xlabel("minorant du temps d'attente pour la sortie (min)")
        retrieval_delays.set_ylabel("part des clients concernés")
        retrieval_delays.set_title("temps d'attente moyen au dépôt")
        retrieval_delays.autoscale(tight=True)

        # ajustement des espaces pour tout afficher
        plt.subplots_adjust(left=0.05,
                    bottom=0.065,
                    right=0.985,
                    top=0.955,
                    wspace=0.175,
                    hspace=0.4)
        plt.show()
        