class Robot():

    def __init__(self, id_robot):

        # arguments cosmétiques
        self.id_robot = id_robot
        self.start_position = (0,0,"bottom")
        self.goal_position = (0,0,"bottom")
        self.goal_time = None
        self.start_time = None

        # arguments utiles
        self.target = None
        self.vehicle = None
    
    def __repr__(self):
        return self.id_robot.__repr__()



