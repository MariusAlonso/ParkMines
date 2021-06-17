import ML_env4
import rl
import datetime

class Brain():
    #sauvegarde model.save, max_stock_visible, number_robots, parking
    

    def __init__(self, model, iterations, max_stock_visible, number_robots, daily_flow, simulation_length):
        self.model = model
        self.max_stock_visible = max_stock_visible
        self.number_robots = number_robots
        self.daily_flow = daily_flow
        self.simulation_length = simulation_length
        self.name = f'models_RL/{iterations}_{datetime.datetime.now().replace(microsecond=0).isoformat().replace(":","-")}'
        self.name_txt = f'models_RL/{iterations}_{datetime.datetime.now().replace(microsecond=0).isoformat().replace(":","-")}.txt'
        # file-append.py
        f = open(self.name_txt,'w')
        write = f'self.max_stock_visible = {self.max_stock_visible} \nself.number_robots = {self.number_robots} \nself.daily_flow = {self.daily_flow} \nself.simulation_length = {self.simulation_length}'
        f.write('\n' + f'{write}')
        f.close()

        model.save(self.name)

    def load(self, name, name_txt):
        pass



        
