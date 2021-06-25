import RL_env
import RL_algorithm
import datetime
from stable_baselines import PPO2

class Brain():

    """
    Classe qui permet de sauvegarder les modèles RL, ainsi que des paramètres fondammentaux 
    (model, iterations, max_stock_visible, number_robots, daily_flow, simulation_length)
    afin de pouvoir les réutiliser.
    Enregistre les modèles dans les fichiers models_RL sous le format timesteps_date-de-l'apprentissage
    """
    def __init__(self):
        pass

    def save(self, model, iterations, max_stock_visible, number_robots, daily_flow, simulation_length):
        """
        Sauvegarde un modèle et les paramètres de l'environnement
        """
        self.model = model
        self.max_stock_visible = max_stock_visible
        self.number_robots = number_robots
        self.daily_flow = daily_flow
        self.simulation_length = simulation_length
        self.name = f'models_RL/{iterations}_{datetime.datetime.now().replace(microsecond=0).isoformat().replace(":","-")}'
        self.name_txt = f'models_RL/{iterations}_{datetime.datetime.now().replace(microsecond=0).isoformat().replace(":","-")}.txt'
        # file-append.py
        f = open(self.name_txt,'w')
        write = f'self.max_stock_visible = \n{self.max_stock_visible} \nself.number_robots = \n{self.number_robots} \nself.daily_flow = \n{self.daily_flow} \nself.simulation_length = \n{self.simulation_length}'
        f.write('\n' + f'{write}')
        f.close()

        model.save(self.name)

    def load(self, name):
        """
        En rentrant le nom du fichier (sans .zip / .txt) renvoie le model et les paramètres adaptés à ce modèle pour créer le env
        """
        name_zip = name + ".zip"
        name_txt = name + ".txt"
        self.model = PPO2.load(name_zip)
        liste = ["None", "None", "self.max_stock_visible", "None", "self.number_robots", "None", "self.daily_flow", "None", "self.simulation_length"]
        with open(name_txt, "r") as fichier:
            for i, line in enumerate(fichier):
                line = line.strip()
                if i == 2:
                    self.max_stock_visible = int(line)
                elif i == 4:
                    self.number_robots = int(line)
                elif i == 6:
                    self.daily_flow = int(line)
                elif i == 8:
                    self.simulation_length = int(line)
        return (self.model, self.max_stock_visible, self.number_robots, self.daily_flow, self.simulation_length)






        
