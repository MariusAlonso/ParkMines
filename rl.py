import heapq
import datetime
import numpy as np
from simulation import Algorithm, Event

def rl_algorithm_builder(model, _dict, number_arguments):

    class RLAlgorithm(Algorithm):

        def __init__(self, simulation, t0, stock, robots, parking, events, *args, print_in_terminal=False):

            super().__init__(simulation, t0, stock, robots, parking, events)

            self.model = model
            if model is None:
                self.reward = 0
            self.current_wake_up = None
            self._dict = _dict
            self.observation = Observation(t0, self.simulation, number_arguments, _dict)
        
        def take_decision(self, action, current_time):
            wake_up_date = self.simulation.t + datetime.timedelta(minutes= 5*(int(action[self._dict("idleness_date")])+1))
            self.current_wake_up = Event(None, wake_up_date, "wake_up_robots", None)
            heapq.heappush(self.events, self.current_wake_up)
            init, end = self._dict("robot_actions_lanes")
            init2, end2 = self._dict("robot_actions_sides", action_space=True)           
            robot_actions_lanes = action[init:end].astype(int)
            robot_actions_sides = action[init2:end2].astype(int)

            for i_robot, robot in enumerate(self.robots):
                
                lane_global_id, side_bool = robot_actions_lanes[i_robot], robot_actions_sides[i_robot]

                if lane_global_id:
                    if self.model is None:
                        self.reward -= 1.
                    if side_bool:
                        side = "bottom"
                    else:
                        side = "top"
                    block_id, lane_id = self.parking.dict_lanes[lane_global_id]
                    robot.goal_position = (block_id, lane_id, side)

                    robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)

                    if robot.vehicle is None:
                        event = Event(None, robot.goal_time, "robot_arrival", robot)
                        #self.parking.blocks[block_id].lanes[lane_id].list_vehicles[0] = 5
                    else:
                        event = Event(robot.vehicle, robot.goal_time, "robot_end_task", robot)
                    robot.doing = event
                    heapq.heappush(self.events, event)
            

    
        def check_pick(self, lane_end, moved_vehicle, current_time):
            return True

        
        def update(self, current_time):
            self.observation.update()
            if self.model is not None:
                action = self.model.predict(self.observation.data)[0]
                self.take_decision(action, self.simulation.t)
            else:
                self.pending_action = True

        def update_retrieval(self, vehicle, success, current_time):
            if self.model is None and success:
                self.reward += 5.
       
        def update_deposit(self, vehicle, success, current_time):
            pass

        def update_robot_arrival(self, robot, lane_end, success, moved_vehicle, current_time):
            self.update(current_time)

        def update_robot_end_task(self, robot, lane_end, success, current_time):
            self.update(current_time)

        def update_start(self):
            self.update(self.t0)
    
    return RLAlgorithm


class Observation():

    def __init__(self, t0, simulation, number_arguments, _dict):

        self.t0 = t0
        self.data = np.zeros((number_arguments, simulation.parking.nb_max_lanes+2))
        self.simulation = simulation
        self._dict = _dict

        for lane_global_id in range(1, self.simulation.parking.number_lanes+1):
            block_id, lane_id = self.simulation.parking.dict_lanes[lane_global_id]
            lane = self.simulation.parking.blocks[block_id].lanes[lane_id]
            if lane.top_position is None:
                self.data[self._dict("lanes_ends", number=lane_global_id), 0:2] = np.array([lane.length//2 + 1, lane.length//2 - 1])
            else:
                self.data[self._dict("lanes_ends", number=lane_global_id), 0:2] = np.array([lane.top_position, lane.bottom_position])

        for i_vehicle, vehicle in enumerate(self.simulation.stock.vehicles.values()):
            deposit_in_sec = (vehicle.deposit - self.t0).total_seconds()
            retrieval_in_sec = (vehicle.retrieval - self.t0).total_seconds()
            self.data[self._dict("stock_dates", number=i_vehicle)] = deposit_in_sec
            self.data[self._dict("stock_dates", number=i_vehicle, retrieval=True)] = retrieval_in_sec
            self.data[self._dict("stock_dates")[0]:number_arguments, 2] = 1
    
    def update(self):

        self.data[self._dict("current_time")] = (self.simulation.t - self.t0).total_seconds()
        
        for i_robot, robot in enumerate(self.simulation.robots):
            if robot.doing is None:
                
                self.data[self._dict("robot_actions_lanes", number=i_robot)] = 0
            else:
                self.data[self._dict("robot_actions_lanes", number=i_robot)] = self.simulation.parking.to_global_id[robot.goal_position[:2]]
                if robot.goal_position[2] == "bottom":
                    self.data[self._dict("robot_actions_sides", number=i_robot)] = 1
                else:
                    self.data[self._dict("robot_actions_sides", number=i_robot)] = 0
                if robot.vehicle is None:
                    self.data[self._dict("robot_actions_is_carrying", number=i_robot)] = 0
                else:
                    self.data[self._dict("robot_actions_is_carrying", number=i_robot)] = 1
                    self.data[self._dict("robot_actions_vehicles", number=i_robot)] = (robot.vehicle.retrieval-self.t0).total_seconds()
        
        for lane_global_id in range(1, self.simulation.parking.number_lanes+1):
            block_id, lane_id = self.simulation.parking.dict_lanes[lane_global_id]
            lane = self.simulation.parking.blocks[block_id].lanes[lane_id]
            if lane.top_position is None:
                self.data[self._dict("lanes_ends", number=lane_global_id),0:2] = np.array([lane.length//2 + 1, lane.length//2 - 1])
            else:
                self.data[self._dict("lanes_ends", number=lane_global_id),0:2] = np.array([lane.top_position, lane.bottom_position])
            for position, vehicle_id in enumerate(lane.list_vehicles):
                if vehicle_id:
                    self.data[self._dict("lanes", number=lane_global_id, place=position)] = (self.simulation.stock.vehicles[vehicle_id].retrieval - self.t0).total_seconds()
                else:
                    self.data[self._dict("lanes", number=lane_global_id, place=position)] = 0