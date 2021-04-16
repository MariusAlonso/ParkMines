from simulation import Simulation
from vehicle import *
import numpy as np

class Analysis():

    def __init__(self, simulation):
        self.simulation = simulation
        self.nb_voiture = {}
        self.taux_occupation = {}
        self.flux_moyen = {}

        self.first_day, self.last_day = self.simulation.stock.duration_simu()
        n = (self.last_day - self.first_day).days #taille de l'axe des abscisses de la figure

        self.nb_entree_array = np.array([None]*n)
        self.nb_sortie_array = np.array([None]*n)
        self.nb_voiture_array = np.array([None]*n)
        self.taux_occupation_array = np.array([None]*n)
        self.flux_moyen_array = np.array([None]*n)

    def entree_vehicle(self):
        for jour in self.simulation.nb_entree.keys():
            self.nb_entree_array[jour] = self.simulation.nb_entree[jour]

    def sortie_vehicle(self):
        for jour in self.simulation.nb_sortie.keys():
            self.nb_sortie_array[jour] = self.simulation.nb_sortie[jour]

    def count_vehicle(self):
        try:
            nb_vehicle = self.simulation.nb_sortie[0] - self.simulation.nb_entree[0]
        except KeyError:
            nb_vehicle = 0

        for jour in self.simulation.nb_entree.keys():
            nb_vehicle = nb_vehicle + self.simulation.nb_entree.get(jour, 0) - self.simulation.nb_sortie.get(jour, 0) 
            self.nb_voiture_array[jour] = nb_vehicle
            self.taux_occupation_array[jour] = 100*nb_vehicle/self.simulation.parking.nb_of_places

    def flux(self):
        for jour in self.simulation.nb_entree.keys():
            self.flux_moyen_array[jour] = self.simulation.nb_entree.get(jour, 0) - self.simulation.nb_sortie.get(jour, 0)