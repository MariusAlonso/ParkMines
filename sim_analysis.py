from simulation import Simulation
from vehicle import *
import numpy as np

class Analysis():

    def __init__(self, simulation):
        self.simulation = simulation
        self.nb_voiture = {}
        self.taux_occupation_parking = {}
        self.taux_occupation_interface = {}
        self.flux_moyen = {}

        self.first_day, self.last_day = self.simulation.stock.duration_simu()
        n = (self.last_day - self.first_day).days #taille de l'axe des abscisses de la figure

        self.nb_entree_array = np.array([None]*n)
        self.nb_sortie_array = np.array([None]*n)
        self.nb_voiture_array = np.array([None]*n)
        self.nb_vehicles_interface_array = np.array([None]*n)
        self.taux_occupation_array = np.array([None]*n)
        self.taux_occupation_interface_array = np.array([None]*n)
        self.flux_moyen_array = np.array([None]*n)

    def entree_vehicle(self):
        L = []
        for jour in self.simulation.nb_entree.keys():
            if L==[]:
                self.nb_entree_array[jour] = self.simulation.nb_entree[jour]
            else :
                self.nb_entree_array[jour] = (self.simulation.nb_entree[jour] + self.simulation.nb_entree[L[-1]])/2
            L.append(jour)
        #print(self.nb_entree_array)

    def sortie_vehicle(self):
        M = []
        for jour in self.simulation.nb_sortie.keys():
            if M == []:
                self.nb_sortie_array[jour] = self.simulation.nb_sortie[jour]
            else :
                self.nb_sortie_array[jour] = (self.simulation.nb_sortie[jour] + self.simulation.nb_sortie[M[-1]])/2
            M.append(jour)
        #print (self.nb_sortie_array, self.simulation.nb_sortie)

    def count_vehicle(self):
        try:
            nb_vehicle = self.simulation.nb_sortie[0] - self.simulation.nb_entree[0]
        except KeyError:
            nb_vehicle = 0

        for jour in self.simulation.nb_sortie.keys():
            nb_vehicle = nb_vehicle + self.simulation.nb_entree.get(jour, 0) - self.simulation.nb_sortie.get(jour, 0) 
            self.nb_voiture_array[jour] = nb_vehicle
            self.taux_occupation_array[jour] = nb_vehicle/self.simulation.parking.nb_of_places

    """
    def count_vehicle_interface(self):
        try:
            nb_vehicle = self.simulation.nb_sortie_interface[0] - self.simulation.nb_entree[0]
        except KeyError:
            nb_vehicle = 0

        for jour in self.simulation.nb_sortie.keys():
            nb_vehicle = nb_vehicle + self.simulation.nb_entree.get(jour, 0) - self.simulation.nb_sortie_interface.get(jour, 0) 
            self.nb_vehicles_interface_array[jour] = nb_vehicle
            self.taux_occupation_interface_array[jour] = nb_vehicle/self.simulation.parking.nb_of_places
    """

    def max_interface(self):    
        for jour in self.simulation.nb_sortie.keys():
            try:
                self.nb_vehicles_interface_array[jour] = self.simulation.nb_vehicles_interface[jour]
            except KeyError:
                self.nb_vehicles_interface_array[jour] = -1

    def flux(self):
        for jour in self.simulation.nb_sortie.keys():
            self.flux_moyen_array[jour] = self.simulation.nb_entree.get(jour, 0) - self.simulation.nb_sortie.get(jour, 0)