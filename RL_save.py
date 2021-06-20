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
        name_zip = name + ".zip"
        name_txt = name + ".txt"
        self.model = PPO2.load(name_zip)
        liste = ["None", "self.max_stock_visible", "None", "self.number_robots", "None", "self.daily_flow", "None", "self.simulation_length"]
        with open(name_txt, "r") as fichier:
            for i, line in enumerate(fichier):
                line = line.strip()
                if line and i%2==1:
                    eval(liste[i] + " = " + line)
        return (self.model, self.max_stock_visible, self.number_robots, self.daily_flow, self.simulation_length)






        
