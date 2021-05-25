from numpy.core.fromnumeric import product
from parking import *
from simulation import *
from inputs import importFromFile
from vehicle import *
from robot import *
import numpy as np
import datetime
from copy import deepcopy
from math import isclose, sqrt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from itertools import product

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
    
    def depositDelaysRates(self, delays=[i for i in range(180)]):
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
    
    def mark(self):
        """
        renvoie la note de la simulation
        """
        retrieval_delays = np.array(self.simulation.retrieval_delays)
        mark = 0
        nb_vehicles = len(self.simulation.stock)

        for delay in range(600):
            mark += pow(np.sum(datetime.timedelta(minutes=delay) < retrieval_delays) - np.sum(datetime.timedelta(minutes=delay+1) < retrieval_delays), 3/2)
        
        mark /= nb_vehicles

        return mark



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
    
    def averageDashboard(self, nb_repetitions=10):
        """
        renvoie les données du Dashboard de la simulation de référence,
        moyennées sur nb_repetitions répétitions
        """
        average_dashboard = {}
        effective_nb_repetitions = 0
        average_intermediate_mpv = 0.
        average_before_deposit_delay = datetime.timedelta()
        average_after_deposit_delay = datetime.timedelta()
        average_retrieval_delay = datetime.timedelta()
        average_deposit_delay_rates = {key: 0. for key in self.delays}
        average_retrieval_delay_rates = {key: 0. for key in self.delays}

        for _ in range(nb_repetitions):
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

                effective_nb_repetitions += 1
        
        for key, value in average_deposit_delay_rates.items():
            average_deposit_delay_rates[key] = value / effective_nb_repetitions
        
        for key, value in average_retrieval_delay_rates.items():
            average_retrieval_delay_rates[key] = value / effective_nb_repetitions

        average_dashboard["average_intermediate_mpv"] = average_intermediate_mpv / effective_nb_repetitions
        average_dashboard["average_before_deposit_delay"] = average_before_deposit_delay / effective_nb_repetitions
        average_dashboard["average_after_deposit_delay"] = average_after_deposit_delay / effective_nb_repetitions
        average_dashboard["average_retrieval_delay"] = average_retrieval_delay / effective_nb_repetitions
        average_dashboard["success_rate"] = effective_nb_repetitions / nb_repetitions
        average_dashboard["average_deposit_delay_rates"] = average_deposit_delay_rates # attention, c'est un dictionnaire
        average_dashboard["average_retrieval_delay_rates"] = average_retrieval_delay_rates # attention, c'est un dictionnaire

        return average_dashboard
    
    def printAverageDashboard(self, nb_repetitions=10):
        """
        affiche les résulats de averageDashboard
        """
        means = self.averageDashboard(nb_repetitions=nb_repetitions)
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

    def variableStockAndRobots(self, nb_repetitions=10, factors=[1+0.1*i for i in range(-4, 3)], nb_robots_max=3):
        """
        regarde l'influence d'une variation du stock sur les différents retards, en moyennant sur nb_repetitions répétitions
        """
        # curves = {(factor, nb_robots): dictionnaire des performances pour ce facteur et ce nombre de robots}
        curves = {}

        # remplissage du dictionnaire curves
        for factor in factors:
            stock_args = tuple(factor*np.array(self.stock_args))
            for nb_robots in range(1, nb_robots_max + 1):
                print(nb_robots, factor)
                # génération de toutes les sorties
                performance = Performance(self.t, stock_args, [Robot(i) for i in range(1, nb_robots + 1)], deepcopy(self.parking), deepcopy(self.algorithm))
                curves[(factor, nb_robots)] = performance.averageDashboard(nb_repetitions)

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
            # façon peu élégante de cadrer la figure
            success_rate.plot(x, [0]*len(x), color='w')
            success_rate.plot(x, [1.1]*len(x), color='w')
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
            if isclose(factor*ref_flow, int(factor*ref_flow)) and int(factor*ref_flow)%2 == 0: #les flux pairs sont un choix arbitraire pour avoir un peu moins de courbes
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
            if isclose(factor*ref_flow, int(factor*ref_flow)) and int(factor*ref_flow)%2 == 0: #les flux pairs sont un choix arbitraire pour avoir un peu moins de courbes
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
                    wspace=0.185,
                    hspace=0.35)
        plt.show()



    def variableInterfaceAndRobots(self, nb_repetitions=10, interface_delta_sizes=[i for i in range(-2, 4)], nb_robots_max=3):
        """
        regarde l'influence d'une variation du stock sur les différents retards, en moyennant sur nb_repetitions répétitions
        """
        # curves = {(interface_size, nb_robots): dictionnaire des performances pour cette taille d'interface et ce nombre de robots}
        curves = {}
        ref_nb_lanes = self.parking.blocks[0].nb_lanes

        # remplissage du dictionnaire curves
        for interface_delta_size in interface_delta_sizes:
            # génération du parking avec la bonne interface
            interface_size = int(ref_nb_lanes+interface_delta_size)
            interface = BlockInterface(None, nb_lanes=interface_size)
            blocks = [interface] + self.parking.blocks[1:]
            disposal = self.parking.disposal[:]
            parking = Parking(blocks, disposal)

            for nb_robots in range(1, nb_robots_max + 1):
                # génération de toutes les sorties
                print(interface_size, nb_robots)
                performance = Performance(self.t, self.stock_args, [Robot(i) for i in range(1, nb_robots + 1)], parking, deepcopy(self.algorithm))
                curves[(interface_size, nb_robots)] = performance.averageDashboard(nb_repetitions)

        # tracé

        ### before deposit ###

        before_deposit = plt.subplot(3, 3, 1)
        # abscisses : la taille de l'interface
        interface_sizes = []
        # ordonnées : liste (indexée par le nombre de robots) des listes de retards
        delay = [[] for i in range(nb_robots)]
        for interface_size, nb_robots in curves:
            if nb_robots == nb_robots_max:
                interface_sizes.append(interface_size)
            delay[nb_robots-1].append(curves[interface_size, nb_robots]['average_before_deposit_delay'])
        # construction des tableaux à tracer
        x = np.array(interface_sizes)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array([duration.total_seconds()/60.0 for duration in delay[nb_robots-1]])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot '
            else:
                label = str(nb_robots) + ' robots'
            before_deposit.plot(x, y, label=label)
        
        # titre et légende
        before_deposit.legend()
        before_deposit.set_xlabel("taille de l'interface")
        before_deposit.set_ylabel("temps d'attente (min)")
        before_deposit.set_title("attente client avant dépôt")
        before_deposit.autoscale(tight=True)

        ### after deposit ###
        
        after_deposit = plt.subplot(3, 3, 2)
        # abscisses : la taille de l'interface
        interface_sizes = []
        # ordonnées : liste (indexée par le nombre de robots) des listes de retards
        delay = [[] for i in range(nb_robots)]
        for interface_size, nb_robots in curves:
            if nb_robots == nb_robots_max:
                interface_sizes.append(interface_size)
            delay[nb_robots-1].append(curves[interface_size, nb_robots]['average_after_deposit_delay'])
        # construction des tableaux à tracer
        x = np.array(interface_sizes)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array([duration.total_seconds()/60.0 for duration in delay[nb_robots-1]])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot'
            else:
                label = str(nb_robots) + ' robots'
            after_deposit.plot(x, y, label=label)
        
        # titre et légende
        after_deposit.legend()
        after_deposit.set_xlabel("taille de l'interface")
        after_deposit.set_ylabel("temps d'attente (min)")
        after_deposit.set_title("attente véhicule dans interface après dépôt")
        after_deposit.autoscale(tight=True)

        ### retrieval ###
        
        retrieval = plt.subplot(3, 3, 3)
        # abscisses : la taille de l'interface
        interface_sizes = []
        # ordonnées : liste (indexée par le nombre de robots) des listes de retards
        delay = [[] for i in range(nb_robots)]
        for interface_size, nb_robots in curves:
            if nb_robots == nb_robots_max:
                interface_sizes.append(interface_size)
            delay[nb_robots-1].append(curves[interface_size, nb_robots]['average_retrieval_delay'])
        # construction des tableaux à tracer
        x = np.array(interface_sizes)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array([duration.total_seconds()/60.0 for duration in delay[nb_robots-1]])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot'
            else:
                label = str(nb_robots) + ' robots'
            retrieval.plot(x, y, label=label)
        
        # titre et légende
        retrieval.legend()
        retrieval.set_xlabel("taille de l'interface")
        retrieval.set_ylabel("temps d'attente (min)")
        retrieval.set_title("attente client avant récupération")
        retrieval.autoscale(tight=True)

        ### average_intermediate_mpv ###
        
        average_intermediate_mpv = plt.subplot(3, 3, 4)
        # abscisses : la taille de l'interface
        interface_sizes = []
        # ordonnées : liste (indexée par le nombre de robots) des nombres de mouvements
        moves = [[] for i in range(nb_robots)]
        for interface_size, nb_robots in curves:
            if nb_robots == nb_robots_max:
                interface_sizes.append(interface_size)
            moves[nb_robots-1].append(curves[interface_size, nb_robots]['average_intermediate_mpv'])
        # construction des tableaux à tracer
        x = np.array(interface_sizes)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array(moves[nb_robots-1])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot'
            else:
                label = str(nb_robots) + ' robots'
            average_intermediate_mpv.plot(x, y, label=label)
        
        # titre et légende
        average_intermediate_mpv.legend()
        average_intermediate_mpv.set_xlabel("taille de l'interface")
        average_intermediate_mpv.set_ylabel("nombre de mouvements")
        average_intermediate_mpv.set_title("nombre de mouvements intermédiaires")
        average_intermediate_mpv.autoscale(tight=True)

        ### success_rate ###
        
        success_rate = plt.subplot(3, 3, 7)
        # abscisses : la taille de l'interface
        interface_sizes = []
        # ordonnées : liste (indexée par le nombre de robots) des taux de succès
        rate = [[] for i in range(nb_robots)]
        for interface_size, nb_robots in curves:
            if nb_robots == nb_robots_max:
                interface_sizes.append(interface_size)
            rate[nb_robots-1].append(curves[interface_size, nb_robots]['success_rate'])
        # construction des tableaux à tracer
        x = np.array(interface_sizes)
        for nb_robots in range(1, nb_robots_max + 1):
            y = np.array(rate[nb_robots-1])
            if nb_robots == 1:
                label = str(nb_robots) + ' robot'
            else:
                label = str(nb_robots) + ' robots'
            # façon peu élégante de cadrer la figure
            success_rate.plot(x, [0]*len(x), color='w')
            success_rate.plot(x, [1.1]*len(x), color='w')
            success_rate.plot(x, y, label=label)
        
        # titre et légende
        success_rate.set_ylim([0., 1.1])
        success_rate.legend()
        success_rate.set_xlabel("taille de l'interface")
        success_rate.set_ylabel("taux de succès")
        success_rate.set_title("taux de succès de l'algorithme")
        success_rate.autoscale(tight=True)

        ### average_deposit_delay_rates ###
        
        deposit_delays = plt.subplot(3, 3, (5, 8))
        
        for interface_size, nb_robots in curves:
            # abscisses : le retard
            delays = []
            # ordonnées : la part des clients concernés
            ratios = []
            # on trace les distributions pour tous les nombres de robots et pour les flux entiers (arbitraire)
            if isclose(interface_size, int(interface_size)):
                #on récupère la courbe pour ce flux et ce nombre de robots
                average_deposit_delay_rates = curves[interface_size, nb_robots]['average_deposit_delay_rates']
                # construction des tableaux à tracer
                for delay, ratio in average_deposit_delay_rates.items():
                    delays.append(delay)
                    ratios.append(ratio)
                
                # tracé
                x = np.array(delays)
                y = np.array(ratios)

                label = f"r={nb_robots}, i={int(interface_size)}"

                deposit_delays.plot(x, y, label=label)        
        
        # titre et légende
        deposit_delays.legend()
        deposit_delays.set_xlabel("minorant du temps d'attente pour la sortie (min)")
        deposit_delays.set_ylabel("part des clients concernés")
        deposit_delays.set_title("temps d'attente moyen au dépôt")
        deposit_delays.autoscale(tight=True)

        ### average_retrieval_delay_rates ###
        
        retrieval_delays = plt.subplot(3, 3, (6, 9))
        
        for interface_size, nb_robots in curves:
            # abscisses : le retard
            delays = []
            # ordonnées : la part des clients concernés
            ratios = []
            # on trace les distributions pour tous les nombres de robots et pour les flux entiers (arbitraire)
            if isclose(interface_size, int(interface_size)):
                #on récupère la courbe pour ce flux et ce nombre de robots
                average_retrieval_delay_rates = curves[interface_size, nb_robots]['average_retrieval_delay_rates']
                # construction des tableaux à tracer
                for delay, ratio in average_retrieval_delay_rates.items():
                    delays.append(delay)
                    ratios.append(ratio)
                
                # tracé
                x = np.array(delays)
                y = np.array(ratios)

                label = f"r={nb_robots}, i={int(interface_size)}"

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
                    wspace=0.185,
                    hspace=0.35)
        plt.show()


    def variableAlgorithmsAndFlow(self, nb_repetitions=10, algorithms=[AlgorithmRandom], factors=[1+0.1*i for i in range(-4, 3)]):
        """
        Compare les performances de différents algorithmes pour un stock variable et différentes durée d'anticipation des sorties
        """
        # curves = {(factor, algorithm): dictionnaire des performances pour ce facteur et ce nombre de robots}
        curves = {}

        # remplissage du dictionnaire curves
        for factor in factors:
            stock_args = tuple(factor*np.array(self.stock_args))
            for algorithm in algorithms:
                print(algorithm.__repr__(), factor)
                # génération de toutes les sorties
                performance = Performance(self.t, stock_args, self.robots, deepcopy(self.parking), deepcopy(algorithm))
                curves[(factor, algorithm)] = performance.averageDashboard(nb_repetitions)

        # tracé
        ref_flow = self.stock_args[0]

        ### before deposit ###

        before_deposit = plt.subplot(3, 3, 1)
        # abscisses : le flow journalier moyen
        flow = []
        # ordonnées : liste (indexée par le nombre de robots) des listes de retards
        delay = {algorithm: [] for algorithm in algorithms}
        for factor, algorithm in curves:
            if algorithm == algorithms[0]:
                flow.append(factor*ref_flow)
            delay[algorithm].append(curves[factor, algorithm]['average_before_deposit_delay'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            y = np.array([duration.total_seconds()/60.0 for duration in delay[algorithm]])
            label = algorithm.__repr__()
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
        delay = {algorithm: [] for algorithm in algorithms}
        for factor, algorithm in curves:
            if algorithm == algorithms[0]:
                flow.append(factor*ref_flow)
            delay[algorithm].append(curves[factor, algorithm]['average_after_deposit_delay'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            y = np.array([duration.total_seconds()/60.0 for duration in delay[algorithm]])
            label = algorithm.__repr__()
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
        delay = {algorithm: [] for algorithm in algorithms}
        for factor, algorithm in curves:
            if algorithm == algorithms[0]:
                flow.append(factor*ref_flow)
            delay[algorithm].append(curves[factor, algorithm]['average_retrieval_delay'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            y = np.array([duration.total_seconds()/60.0 for duration in delay[algorithm]]) 
            label = algorithm.__repr__()
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
        moves = {algorithm: [] for algorithm in algorithms}
        for factor, algorithm in curves:
            if algorithm == algorithms[0]:
                flow.append(factor*ref_flow)
            moves[algorithm].append(curves[factor, algorithm]['average_intermediate_mpv'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            y = np.array(moves[algorithm])
            label = algorithm.__repr__()
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
        rate = {algorithm: [] for algorithm in algorithms}
        for factor, algorithm in curves:
            if algorithm == algorithms[0]:
                flow.append(factor*ref_flow)
            rate[algorithm].append(curves[factor, algorithm]['success_rate'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            y = np.array(rate[algorithm])
            label = algorithm.__repr__()
            # façon peu élégante de cadrer la figure
            success_rate.plot(x, [0]*len(x), color='w')
            success_rate.plot(x, [1.1]*len(x), color='w')
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
        
        for factor, algorithm in curves:
            # abscisses : le retard
            delays = []
            # ordonnées : la part des clients concernés
            ratios = []
            # on trace les distributions pour tous les nombres de robots et pour les flux entiers (arbitraire)
            if isclose(factor, 1): # on ne garde qu'un flux pour avoir un peu moins de courbes
                #on récupère la courbe pour ce flux et ce nombre de robots
                average_deposit_delay_rates = curves[factor, algorithm]['average_deposit_delay_rates']
                # construction des tableaux à tracer
                for delay, ratio in average_deposit_delay_rates.items():
                    delays.append(delay)
                    ratios.append(ratio)
                
                # tracé
                x = np.array(delays)
                y = np.array(ratios)

                label = f"{algorithm.__repr__()}, f={int(factor*ref_flow)}"

                deposit_delays.plot(x, y, label=label)        
        
        # titre et légende
        deposit_delays.legend()
        deposit_delays.set_xlabel("minorant du temps d'attente pour la sortie (min)")
        deposit_delays.set_ylabel("part des clients concernés")
        deposit_delays.set_title("temps d'attente moyen au dépôt")
        deposit_delays.autoscale(tight=True)

        ### average_retrieval_delay_rates ###
        
        retrieval_delays = plt.subplot(3, 3, (6, 9))
        
        for factor, algorithm in curves:
            # abscisses : le retard
            delays = []
            # ordonnées : la part des clients concernés
            ratios = []
            # on trace les distributions pour tous les nombres de robots et pour les flux entiers (arbitraire)
            if isclose(factor, 1): # on ne garde qu'un flux pour avoir un peu moins de courbes
                #on récupère la courbe pour ce flux et ce nombre de robots
                average_retrieval_delay_rates = curves[factor, algorithm]['average_retrieval_delay_rates']
                # construction des tableaux à tracer
                for delay, ratio in average_retrieval_delay_rates.items():
                    delays.append(delay)
                    ratios.append(ratio)
                
                # tracé
                x = np.array(delays)
                y = np.array(ratios)

                label = f"{algorithm.__repr__()}, f={int(factor*ref_flow)}"

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
                    wspace=0.185,
                    hspace=0.35)
        plt.show()

    def variableAlgorithmsAnticipationTimeAndFlow(self, nb_repetitions=10, algorithms=[AlgorithmRandom], factors=[1+0.1*i for i in range(-4, 3)], anticipation_times=[datetime.timedelta(hours=1), datetime.timedelta(hours=4), datetime.timedelta(hours=8)]):
        """
        Compare les performances de différents algorithmes pour un stock variable et différentes durée d'anticipation des sorties
        """
        # curves = {(factor, algorithm): dictionnaire des performances pour ce facteur et ce nombre de robots}
        curves = {}

        # remplissage du dictionnaire curves
        for factor in factors:
            stock_args = tuple(factor*np.array(self.stock_args))
            for algorithm in algorithms:
                for anticipation_time in anticipation_times:
                    print(algorithm.__repr__(), factor, anticipation_time.total_seconds()/3600)
                    # génération de toutes les sorties
                    performance = Performance(self.t, stock_args, self.robots, deepcopy(self.parking), deepcopy(algorithm))
                    curves[(factor, algorithm, anticipation_time)] = performance.averageDashboard(nb_repetitions)

        # tracé
        ref_flow = self.stock_args[0]

        ### before deposit ###

        before_deposit = plt.subplot(3, 3, 1)
        # abscisses : le flow journalier moyen
        flow = []
        # ordonnées : liste (indexée par le nombre de robots) des listes de retards
        delay = {(algorithm, anticipation_time): [] for algorithm, anticipation_time in product(algorithms, anticipation_times)}
        for factor, algorithm, anticipation_time in curves:
            if algorithm == algorithms[0] and anticipation_time == anticipation_times[0]:
                flow.append(factor*ref_flow)
            delay[algorithm, anticipation_time].append(curves[factor, algorithm, anticipation_time]['average_before_deposit_delay'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            for anticipation_time in anticipation_times:
                y = np.array([duration.total_seconds()/60.0 for duration in delay[algorithm, anticipation_time]])
                label = algorithm.__repr__() + " " + str(anticipation_time.total_seconds()//3600)
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
        delay = {(algorithm, anticipation_time): [] for algorithm, anticipation_time in product(algorithms, anticipation_times)}
        for factor, algorithm, anticipation_time in curves:
            if algorithm == algorithms[0] and anticipation_time == anticipation_times[0]:
                flow.append(factor*ref_flow)
            delay[algorithm, anticipation_time].append(curves[factor, algorithm, anticipation_time]['average_after_deposit_delay'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            for anticipation_time in anticipation_times:
                y = np.array([duration.total_seconds()/60.0 for duration in delay[algorithm, anticipation_time]])
                label = algorithm.__repr__() + " " + str(anticipation_time.total_seconds()//3600)
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
        delay = {(algorithm, anticipation_time): [] for algorithm, anticipation_time in product(algorithms, anticipation_times)}
        for factor, algorithm, anticipation_time in curves:
            if algorithm == algorithms[0] and anticipation_time == anticipation_times[0]:
                flow.append(factor*ref_flow)
            delay[algorithm, anticipation_time].append(curves[factor, algorithm, anticipation_time]['average_retrieval_delay'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            for anticipation_time in anticipation_times:
                y = np.array([duration.total_seconds()/60.0 for duration in delay[algorithm, anticipation_time]]) 
                label = algorithm.__repr__() + str(anticipation_time.total_seconds()//3600)
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
        moves = {(algorithm, anticipation_time): [] for algorithm, anticipation_time in product(algorithms, anticipation_times)}
        for factor, algorithm, anticipation_time in curves:
            if algorithm == algorithms[0] and anticipation_time == anticipation_times[0]:
                flow.append(factor*ref_flow)
            moves[algorithm, anticipation_time].append(curves[factor, algorithm, anticipation_time]['average_intermediate_mpv'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            for anticipation_time in anticipation_times:
                y = np.array(moves[algorithm, anticipation_time])
                label = algorithm.__repr__() + " " + str(anticipation_time.total_seconds()//3600)
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
        rate = {(algorithm, anticipation_time): [] for algorithm, anticipation_time in product(algorithms, anticipation_times)}
        for factor, algorithm, anticipation_time in curves:
            if algorithm == algorithms[0] and anticipation_time == anticipation_times[0]:
                flow.append(factor*ref_flow)
            rate[algorithm, anticipation_time].append(curves[factor, algorithm, anticipation_time]['success_rate'])
        # construction des tableaux à tracer
        x = np.array(flow)
        for algorithm in algorithms:
            for anticipation_time in anticipation_times:
                y = np.array(rate[algorithm, anticipation_time])
                label = algorithm.__repr__() + " " + str(anticipation_time.total_seconds()//3600)
                # façon peu élégante de cadrer la figure
                success_rate.plot(x, [0]*len(x), color='w')
                success_rate.plot(x, [1.1]*len(x), color='w')
                success_rate.plot(x, y, label=label)
        
        # titre et légende
        success_rate.set_ylim([0., 1.1])
        success_rate.legend()
        success_rate.set_xlabel("flux journalier moyen")
        success_rate.set_ylabel("taux de succès")
        success_rate.set_title("taux de succès de l'algorithme")
        success_rate.autoscale(tight=True)

        """
        ### average_deposit_delay_rates ###
        
        deposit_delays = plt.subplot(3, 3, (5, 8))
        
        for factor, algorithm, anticipation_time in curves:
            # abscisses : le retard
            delays = []
            # ordonnées : la part des clients concernés
            ratios = []
            # on trace les distributions pour tous les nombres de robots et pour les flux entiers (arbitraire)
            if isclose(factor, 1): # on ne garde qu'un flux pour avoir un peu moins de courbes
                #on récupère la courbe pour ce flux et ce nombre de robots
                average_deposit_delay_rates = curves[factor, algorithm, anticipation_time]['average_deposit_delay_rates']
                # construction des tableaux à tracer
                for delay, ratio in average_deposit_delay_rates.items():
                    delays.append(delay)
                    ratios.append(ratio)
                
                # tracé
                x = np.array(delays)
                y = np.array(ratios)

                label = f"{algorithm.__repr__()}, {(anticipation_time.total_seconds()//3600)}h, f={int(factor*ref_flow)}"

                deposit_delays.plot(x, y, label=label)        
        
        # titre et légende
        deposit_delays.legend()
        deposit_delays.set_xlabel("minorant du temps d'attente pour la sortie (min)")
        deposit_delays.set_ylabel("part des clients concernés")
        deposit_delays.set_title("temps d'attente moyen au dépôt")
        deposit_delays.autoscale(tight=True)
        """

        ### average_retrieval_delay_rates ###
        
        retrieval_delays = plt.subplot(3, 3, (5, 9))
        
        for factor, algorithm, anticipation_time in curves:
            # abscisses : le retard
            delays = []
            # ordonnées : la part des clients concernés
            ratios = []
            # on trace les distributions pour tous les nombres de robots et pour les flux entiers (arbitraire)
            if isclose(factor, 1): # on ne garde qu'un flux pour avoir un peu moins de courbes
                #on récupère la courbe pour ce flux et ce nombre de robots
                average_retrieval_delay_rates = curves[factor, algorithm, anticipation_time]['average_retrieval_delay_rates']
                # construction des tableaux à tracer
                for delay, ratio in average_retrieval_delay_rates.items():
                    delays.append(delay)
                    ratios.append(ratio)
                
                # tracé
                x = np.array(delays)
                y = np.array(ratios)

                label = f"{algorithm.__repr__()}, {anticipation_time.total_seconds()//3600}h, f={int(factor*ref_flow)}"

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
                    wspace=0.185,
                    hspace=0.35)
        plt.show()


    def algorithmMark(self, nb_repetitions=100, optimization_parameters=None):
        """
        calcule la "note" de l'algorithme : somme(retards^3/2)/nb_véhicules, moyennée sur nb_repetitions simulations
        """
        effective_nb_repetitions = 0
        average_mark = 0

        for _ in range(nb_repetitions):
            simulation = Simulation(self.t, RandomStock(*self.stock_args), deepcopy(self.robots), deepcopy(self.parking), deepcopy(self.algorithm), optimization_parameters=optimization_parameters)
            dashboard = Dashboard(simulation)
            if dashboard.completed:     # indique si on a réussi a aller au bout de la simulation
                
                average_mark += dashboard.mark()
                effective_nb_repetitions += 1

        try:
            average_mark /= effective_nb_repetitions
        except ZeroDivisionError:
            average_mark = 1000

        return average_mark

    def algorithmMarkOnPool(self, optimization_parameters=None):
        """
        calcule la "note" de l'algorithme : somme(retards^3/2)/nb_véhicules, moyennée sur le pool de stocks
        """
        effective_nb_repetitions = 0
        average_mark = 0
        root_path = "C:/Users/LOUIS/mines/ParkMines/inputs/pool_for_optim/"

        for i in range(10):
            path = root_path + 'stock_' + str(i) + '.csv'
            simulation = Simulation(self.t, Stock(importFromFile(path=path)), deepcopy(self.robots), deepcopy(self.parking), deepcopy(self.algorithm), optimization_parameters=optimization_parameters)
            dashboard = Dashboard(simulation)
            if dashboard.completed:     # indique si on a réussi a aller au bout de la simulation
                
                average_mark += dashboard.mark()
                effective_nb_repetitions += 1

        try:
            average_mark /= effective_nb_repetitions
        except ZeroDivisionError:
            average_mark = 1000

        return average_mark


    def refineParametersZeroMinus(self, variation_coef=0.9, nb_steps=10, nb_repetitions=100, initial_parameters=[1., 1.1, 20., -5.]):
        """
        Affine les paramètres de 0- sur nb_repetitions
        """
        best_optimization_parameters = initial_parameters

        # dictionnaire : (alpha, beta, start_new_lane_weight, distance_to_lane_end_coef) : score pour les simulations réalisées
        marks = {}

        for k in range(nb_steps):
            print(f"step {k} :")
            # création d'un dictionnaire des notes "locales" et ajout de la référence
            local_marks = {}
            best_optimization_parameters = list(best_optimization_parameters)
            mark = self.algorithmMark(nb_repetitions, optimization_parameters=best_optimization_parameters)
            local_marks[tuple(best_optimization_parameters)] = mark
            # parcours des jeux de paramètres adjacents
            for i in range(len(best_optimization_parameters)):
                # on essaie en diminuant un peu le i-ème paramètre
                parameters = best_optimization_parameters[:]
                parameters[i] *= variation_coef
                # calcul de la note
                mark = self.algorithmMark(nb_repetitions, optimization_parameters=parameters)
                marks[tuple(parameters)] = mark
                local_marks[tuple(parameters)] = mark
                #print(f"{tuple(parameters)} : {mark}")

                # on essaie en aumentant un peu le i-ème paramètre
                parameters = best_optimization_parameters[:]
                parameters[i] /= variation_coef
                # calcul de la note
                mark = self.algorithmMark(nb_repetitions, optimization_parameters=parameters)
                marks[tuple(parameters)] = mark
                local_marks[tuple(parameters)] = mark
                #print(f"{tuple(parameters)} : {mark}")

            # mise à jour des paramètres de référence
            best_mark = local_marks[tuple(best_optimization_parameters)]
            for parameters, mark in local_marks.items():
                if mark < best_mark:
                    best_optimization_parameters = parameters
                    best_mark = mark
            print(f"{best_optimization_parameters} : {best_mark}")
        return marks

    def refineParametersZeroMinusOnPool(self, low_variation_coef=0.5, high_variation_coef=0.9, nb_steps=10, initial_parameters=[1., 3., 100., -10.]):
        """
        Affine les paramètres de 0- sur nb_repetitions
        """
        best_optimization_parameters = initial_parameters
        variation_coef = sqrt(low_variation_coef*high_variation_coef)

        # dictionnaire : (alpha, beta, start_new_lane_weight, distance_to_lane_end_coef) : score pour les simulations réalisées
        marks = {}
        # liste des points parcourus lors de la pseudo-descente (avec les notes et coefficients de variation associés)
        path = []

        for k in range(nb_steps):
            print(f"step {k} :")
            # création d'un dictionnaire des notes "locales" et ajout de la référence
            local_marks = {}
            best_optimization_parameters = list(best_optimization_parameters)
            best_mark = self.algorithmMarkOnPool(optimization_parameters=best_optimization_parameters)
            local_marks[tuple(best_optimization_parameters)] = best_mark
            print(f"{best_optimization_parameters} : {best_mark}")
            # parcours des jeux de paramètres adjacents
            for i in range(len(best_optimization_parameters)):
                # on essaie en diminuant un peu le i-ème paramètre
                parameters = best_optimization_parameters[:]
                parameters[i] *= variation_coef
                # calcul de la note
                mark = self.algorithmMarkOnPool(optimization_parameters=parameters)
                marks[tuple(parameters)] = mark
                local_marks[tuple(parameters)] = mark
                print(f"{tuple(parameters)} : {mark}")

                # on essaie en aumentant un peu le i-ème paramètre
                parameters = best_optimization_parameters[:]
                parameters[i] /= variation_coef
                # calcul de la note
                mark = self.algorithmMarkOnPool(optimization_parameters=parameters)
                marks[tuple(parameters)] = mark
                local_marks[tuple(parameters)] = mark
                print(f"{tuple(parameters)} : {mark}")

            # mise à jour des paramètres de référence
            best_mark = local_marks[tuple(best_optimization_parameters)]
            changed = False
            for parameters, mark in local_marks.items():
                if mark < best_mark:
                    changed = True
                    best_optimization_parameters = parameters
                    best_mark = mark
            path.append((best_optimization_parameters, best_mark, variation_coef))
            
            # si on arrive à améliorer le coût : on rapproche le coefficient de variation de la cible haute (proche de 1)
            if changed:
                variation_coef = sqrt(variation_coef*high_variation_coef)
            # si on n'arrive pas à améliorer le coût, i.e. on est dans un minimum local : on rapproche le coefficient de variation de la cible basse (plus proche de 0)
            else:
                variation_coef = sqrt(variation_coef*low_variation_coef)
        return marks, path

    def cutViewZeroMinusOnPool(self, start=0.5, stop=10, step=0.5, other_parameters=[100., -10.]):
        """
        calcule le score pour une gamme de valeurs ded alpha et beta
        """

        # dictionnaire : (alpha, beta, start_new_lane_weight, distance_to_lane_end_coef) : score pour les simulations réalisées
        marks = {}

        for alpha in [start+n*step for n in range(int((stop-start)/step))]:
            for beta in [start+n*step for n in range(int((stop-start)/step))]:
                if alpha < beta:
                    optimization_parameters = [alpha, beta] + other_parameters
                    mark = self.algorithmMarkOnPool(optimization_parameters=optimization_parameters)
                    print(f"{tuple(optimization_parameters)} : {mark:.3f}")
                    marks[tuple(optimization_parameters)] = mark
        return marks
    
    def logCutViewZeroMinusOnPool(self, start=-3, stop=5, step=1, other_parameters=[100., -10.]):
        """
        calcule le score pour une gamme de valeurs ded alpha et beta
        """

        # dictionnaire : (alpha, beta, start_new_lane_weight, distance_to_lane_end_coef) : score pour les simulations réalisées
        marks = {}

        for log_alpha in range(start, stop, step):
            for log_beta in range(log_alpha, stop, step):
                alpha = 1.2**log_alpha
                beta = 1.2**log_beta
                if alpha < beta:
                    optimization_parameters = [alpha, beta] + other_parameters
                    mark = self.algorithmMarkOnPool(optimization_parameters=optimization_parameters)
                    print(f"{tuple(optimization_parameters)} : {mark:.3f}")
                    marks[tuple(optimization_parameters)] = mark
        return marks