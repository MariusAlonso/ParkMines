import heapq
import datetime
import numpy as np
from numpy.core.numerictypes import maximum_sctype
from simulation import Algorithm, Event


def rl_algorithm_builder(model, _dict, number_arguments, max_stock_visible, print_action=False):

    class RLAlgorithm(Algorithm):

        def __init__(self, simulation, t0, stock, robots, parking, events, *args, print_in_terminal=False):

            super().__init__(simulation, t0, stock, robots, parking, events)

            self.model = model
            if model is None:
                self.reward = 0
            self.current_wake_up = None
            self._dict = _dict
            self.observation = Observation(t0, self.simulation, number_arguments, _dict, max_stock_visible)
        
        def take_decision(self, action, current_time):
            if print_action:
                print(action)
            init, end = self._dict("robot_pick_lane", action_space=True)
            init2, end2 = self._dict("robot_pick_side", action_space=True)
            init3, end3 = self._dict("robot_drop_lane", action_space=True) 
            init4, end4 = self._dict("robot_drop_side", action_space=True)  
            robot_action = action[1:(len(self.robots)+1)]     
            robot_pick_lane = action[init:end].astype(int) + 1
            robot_pick_side = action[init2:end2].astype(int)
            robot_drop_lane = action[init3:end3].astype(int) + 1
            robot_drop_side = action[init4:end4].astype(int)

            need_wake_up = True

            for i_robot, robot in enumerate(self.robots):

                if robot_action[i_robot]:

                    if robot.doing is None and robot.vehicle is None:
                        
                        lane_global_id, side_bool = robot_pick_lane[i_robot], robot_pick_side[i_robot]

                        if lane_global_id < self.parking.number_lanes:

                            if side_bool:
                                side = "bottom"
                            else:
                                side = "top"
                            block_id, lane_id = self.parking.dict_lanes[lane_global_id]
                            robot.goal_position = (block_id, lane_id, side)

                            robot.start_time = current_time
                            robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)

                            event = Event(None, robot.goal_time, "robot_arrival", robot)
                            robot.doing = event
                            self.events.add(event)
                            need_wake_up = False

                            lane_global_id, side_bool = robot_drop_lane[i_robot], robot_drop_side[i_robot]

                            if lane_global_id < self.parking.number_lanes:

                                if side_bool:
                                    side = "bottom"
                                else:
                                    side = "top"
                                block_id, lane_id = self.parking.dict_lanes[lane_global_id]
                                robot.drop_position = (block_id, lane_id, side)
                            
                            else:
                                robot.drop_position = None
                    
                    elif robot.doing is None:

                        lane_global_id, side_bool = robot_drop_lane[i_robot], robot_drop_side[i_robot]

                        if lane_global_id < self.parking.number_lanes:
                            if side_bool:
                                side = "bottom"
                            else:
                                side = "top"
                            block_id, lane_id = self.parking.dict_lanes[lane_global_id]
                            robot.goal_position = (block_id, lane_id, side)

                            robot.start_time = current_time
                            robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)

                            event = Event(robot.vehicle, robot.goal_time, "robot_end_task", robot)

                            robot.doing = event
                            self.events.add(event)  
                            need_wake_up = False

                if need_wake_up and self.simulation.vehicles_left_to_handle:
                    # print(len(self.simulation.retrievals_in_parking) + len(self.simulation.deposit_events), len(self.simulation.vehicles_left_to_handle))

                    if self.simulation.retrievals_in_parking:
                        next_event = self.simulation.retrievals_in_parking[-1].retrieval
                        if self.simulation.deposit_events:
                            next_event = min(next_event, self.simulation.deposit_events[-1].date)
                    else:
                        next_event = self.simulation.deposit_events[-1].date
                    
                    wake_up_date = max(self.simulation.t + datetime.timedelta(minutes=5), next_event - datetime.timedelta(minutes=(int(action[self._dict("idleness_date")])*5)**2))
                    self.current_wake_up = Event(None, wake_up_date, "wake_up_robots", None)
                    self.events.add(self.current_wake_up)
                else:
                    self.current_wake_up = None
                    
    
        def check_pick(self, lane_end, moved_vehicle, current_time):
            return True

        
        def update(self, current_time):
            self.observation.update()
            if self.model is not None:
                action = self.model.predict(self.observation.data)[0]
                self.take_decision(action, self.simulation.t)
            else:
                self.reward -= 25
                self.pending_action = True

        def update_retrieval(self, vehicle, success, current_time):
            if self.model is None and success:
                self.reward += 100.*(10/len(self.stock))
                if vehicle.retrieval == current_time:
                    self.reward += 400.*(10/len(self.stock))
       
        def update_deposit(self, vehicle, success, current_time):
            if self.model is None and success:
                self.reward += 100.*(10/len(self.stock))
                if vehicle.deposit == current_time:
                    self.reward += 400.*(10/len(self.stock))
            pass

        def update_robot_arrival(self, robot, lane_end, success, moved_vehicle, current_time):
            if success and robot.drop_position is not None:

                robot.goal_position = robot.drop_position

                robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)

                event = Event(robot.vehicle, robot.goal_time, "robot_end_task", robot)

                robot.doing = event
                self.events.add(event)   
            else:
                self.update(current_time)

            if self.model is None:
                if success:
                    self.reward += 0   
                else:
                    self.reward -= 5    

        def update_robot_end_task(self, robot, lane_end, success, current_time):
            self.reward += 25
            self.update(current_time)
        
            if self.model is None:
                if success:
                    self.reward += 0
                else:
                    self.reward -= 5  

        def update_start(self):
            self.update(self.t0)
    
    return RLAlgorithm

"""
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
                
                self.data[self._dict("robot_pick_lane", number=i_robot)] = 0
            else:
                self.data[self._dict("robot_pick_lane", number=i_robot)] = self.simulation.parking.to_global_id[robot.goal_position[:2]]
                self.data[self._dict("robot_pick_side", number=i_robot)] = int(robot.goal_position[2] == "bottom")
                
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
                    self.data[self._dict("lanes", number=lane_global_id, place=position)] = (self.simulation.stock.vehicles[vehicle_id].retrieval - self.simulation.t).total_seconds()
                else:
                    self.data[self._dict("lanes", number=lane_global_id, place=position)] = 0
        
        for i_vehicle, vehicle in enumerate(self.simulation.stock.vehicles.values()):
            deposit_in_sec = (vehicle.deposit - self.simulation.t).total_seconds()
            retrieval_in_sec = (vehicle.retrieval - self.simulation.t).total_seconds()
            self.data[self._dict("stock_dates", number=i_vehicle)] = deposit_in_sec
            self.data[self._dict("stock_dates", number=i_vehicle, retrieval=True)] = retrieval_in_sec
"""

class ObservationBis():

    def __init__(self, t0, simulation, number_arguments, _dict, max_stock_visible):

        self.t0 = t0
        self.data = np.zeros((number_arguments, simulation.parking.longest_lane+2))
        self.simulation = simulation
        self._dict = _dict
        self.number_arguments = number_arguments
        self.max_stock_visible = max_stock_visible

        for lane_global_id in range(1, self.simulation.parking.number_lanes+1):
            block_id, lane_id = self.simulation.parking.dict_lanes[lane_global_id]
            lane = self.simulation.parking.blocks[block_id].lanes[lane_id]
            if lane.top_position is None:
                self.data[self._dict("lanes_ends", number=lane_global_id), 0:2] = np.array([lane.length//2 + 1, lane.length//2 - 1])
            else:
                self.data[self._dict("lanes_ends", number=lane_global_id), 0:2] = np.array([lane.top_position, lane.bottom_position])

        for i in range(self.max_stock_visible):
            if i < len(self.simulation.deposit_events):
                vehicle = self.simulation.deposit_events[-i-1].vehicle
                deposit_in_sec = (vehicle.deposit - self.simulation.t).total_seconds()
                retrieval_in_sec = (vehicle.retrieval - self.simulation.t).total_seconds()
                self.data[self._dict("stock_dates", number=i)] = deposit_in_sec
                self.data[self._dict("stock_dates", number=i, retrieval=True)] = retrieval_in_sec
                self.data[self._dict("stock_dates", number=i)[0], 2] = 1
            else:
                self.data[self._dict("stock_dates", number=i)[0], 2] = 0
    
    def update(self):
        
        for i_robot, robot in enumerate(self.simulation.robots):

            if robot.doing is None:
                self.data[self._dict("robot_pick_lane", number=i_robot)] = 0
            else:
                self.data[self._dict("robot_pick_lane", number=i_robot)] = self.simulation.parking.to_global_id[robot.goal_position[:2]]
                self.data[self._dict("robot_pick_side", number=i_robot)] = int(robot.goal_position[2] == "bottom")

                if robot.drop_position is None:
                    self.data[self._dict("robot_drop_lane", number=i_robot)] = 0
                else:
                    self.data[self._dict("robot_drop_lane", number=i_robot)] = self.simulation.parking.to_global_id[robot.drop_position[:2]]
                    self.data[self._dict("robot_drop_side", number=i_robot)] = int(robot.drop_position[2] == "bottom")

            if robot.vehicle is None:
                self.data[self._dict("robot_actions_is_carrying", number=i_robot)] = 0
            else:
                self.data[self._dict("robot_actions_is_carrying", number=i_robot)] = 1
                self.data[self._dict("robot_actions_vehicles", number=i_robot)] = (robot.vehicle.retrieval-self.simulation.t).total_seconds()
 

        
        for lane_global_id in range(1, self.simulation.parking.number_lanes+1):
            block_id, lane_id = self.simulation.parking.dict_lanes[lane_global_id]
            lane = self.simulation.parking.blocks[block_id].lanes[lane_id]
            if lane.top_position is None:
                self.data[self._dict("lanes_ends", number=lane_global_id),0:2] = np.array([lane.length//2 + 1, lane.length//2 - 1])
            else:
                self.data[self._dict("lanes_ends", number=lane_global_id),0:2] = np.array([lane.top_position, lane.bottom_position])
            for position, vehicle_id in enumerate(lane.list_vehicles):
                if vehicle_id:
                    self.data[self._dict("lanes", number=lane_global_id, place=position)] = (self.simulation.stock.vehicles[vehicle_id].retrieval - self.simulation.t).total_seconds()
                else:
                    self.data[self._dict("lanes", number=lane_global_id, place=position)] = 0
        
        for i in range(self.max_stock_visible):
            if i < len(self.simulation.deposit_events):
                vehicle = self.simulation.deposit_events[-i-1].vehicle
                deposit_in_sec = (vehicle.deposit - self.simulation.t).total_seconds()
                retrieval_in_sec = (vehicle.retrieval - self.simulation.t).total_seconds()
                self.data[self._dict("stock_dates", number=i)] = deposit_in_sec
                self.data[self._dict("stock_dates", number=i, retrieval=True)] = retrieval_in_sec
                self.data[self._dict("stock_dates", number=i)[0], 2] = 1
            else:
                self.data[self._dict("stock_dates", number=i)[0], 2] = 0

class Observation():

    def __init__(self, t0, simulation, number_arguments, _dict, max_stock_visible):

        self.t0 = t0
        self.data = np.zeros((number_arguments, max(simulation.parking.longest_lane+2, 7)))
        self.simulation = simulation
        self._dict = _dict
        self.number_arguments = number_arguments
        self.max_stock_visible = max_stock_visible

        for lane_global_id in range(1, self.simulation.parking.number_lanes+1):
            block_id, lane_id = self.simulation.parking.dict_lanes[lane_global_id]
            lane = self.simulation.parking.blocks[block_id].lanes[lane_id]
            if lane.top_position is None:
                self.data[self._dict("lanes_ends", number=lane_global_id), 0:2] = np.array([lane.length, lane.length])
            else:
                self.data[self._dict("lanes_ends", number=lane_global_id), 0:2] = np.array([lane.top_position, lane.length-lane.bottom_position-1])

        for i in range(self.max_stock_visible):
            if i < len(self.simulation.deposit_events):
                vehicle = self.simulation.deposit_events[-i-1].vehicle
                deposit_in_sec = (vehicle.deposit - self.simulation.t).total_seconds()
                retrieval_in_sec = (vehicle.retrieval - self.simulation.t).total_seconds()
                self.data[self._dict("stock_dates", number=i)] = deposit_in_sec
                self.data[self._dict("stock_dates", number=i, retrieval=True)] = retrieval_in_sec
                self.data[self._dict("stock_dates", number=i)[0], 2] = 1
            else:
                self.data[self._dict("stock_dates", number=i)[0], 2] = 0
    
        for i in range(self.max_stock_visible):
            if i < len(self.simulation.retrievals_in_parking):
                vehicle = self.simulation.retrievals_in_parking[-i-1]
                retrieval_in_sec = (vehicle.retrieval - self.simulation.t).total_seconds()
                self.data[self._dict("stock_dates", number=i)[0], 3] = retrieval_in_sec
                if vehicle.id in self.simulation.parking.occupation:
                    block_id, lane_id, position = self.simulation.parking.occupation[vehicle.id]
                    self.data[self._dict("stock_dates", number=i)[0], 4] = self.simulation.parking.to_global_id[(block_id, lane_id)]
                    self.data[self._dict("stock_dates", number=i)[0], 5] = position
                else:
                    self.data[self._dict("stock_dates", number=i)[0], 4] = 0
                    self.data[self._dict("stock_dates", number=i)[0], 5] = 0                  
                self.data[self._dict("stock_dates", number=i)[0], 6] = 1
            else:
                self.data[self._dict("stock_dates", number=i)[0], 6] = 0
    
    def update(self):
        
        for i_robot, robot in enumerate(self.simulation.robots):

            if robot.doing is None:
                self.data[self._dict("robot_pick_lane", number=i_robot)] = 0
            else:
                self.data[self._dict("robot_pick_lane", number=i_robot)] = self.simulation.parking.to_global_id[robot.goal_position[:2]]
                self.data[self._dict("robot_pick_side", number=i_robot)] = int(robot.goal_position[2] == "bottom")

                if robot.drop_position is None:
                    self.data[self._dict("robot_drop_lane", number=i_robot)] = 0
                else:
                    self.data[self._dict("robot_drop_lane", number=i_robot)] = self.simulation.parking.to_global_id[robot.drop_position[:2]]
                    self.data[self._dict("robot_drop_side", number=i_robot)] = int(robot.drop_position[2] == "bottom")

            if robot.vehicle is None:
                self.data[self._dict("robot_actions_is_carrying", number=i_robot)] = 0
            else:
                self.data[self._dict("robot_actions_is_carrying", number=i_robot)] = 1
                self.data[self._dict("robot_actions_vehicles", number=i_robot)] = (robot.vehicle.retrieval-self.simulation.t).total_seconds()
 

        
        for lane_global_id in range(1, self.simulation.parking.number_lanes+1):
            block_id, lane_id = self.simulation.parking.dict_lanes[lane_global_id]
            lane = self.simulation.parking.blocks[block_id].lanes[lane_id]
            if lane.top_position is None:
                self.data[self._dict("lanes_ends", number=lane_global_id),0:2] = np.array([lane.length, lane.length])
            else:
                self.data[self._dict("lanes_ends", number=lane_global_id),0:2] = np.array([lane.top_position, lane.length-lane.bottom_position-1])
            for position, vehicle_id in enumerate(lane.list_vehicles):
                if vehicle_id:
                    self.data[self._dict("lanes", number=lane_global_id, place=position)] = (self.simulation.stock.vehicles[vehicle_id].retrieval - self.simulation.t).total_seconds()
                else:
                    self.data[self._dict("lanes", number=lane_global_id, place=position)] = 0
        
        for i in range(self.max_stock_visible):
            if i < len(self.simulation.deposit_events):
                vehicle = self.simulation.deposit_events[-i-1].vehicle
                deposit_in_sec = (vehicle.deposit - self.simulation.t).total_seconds()
                retrieval_in_sec = (vehicle.retrieval - self.simulation.t).total_seconds()
                self.data[self._dict("stock_dates", number=i)] = deposit_in_sec
                self.data[self._dict("stock_dates", number=i, retrieval=True)] = retrieval_in_sec
                self.data[self._dict("stock_dates", number=i)[0], 2] = 1
            else:
                self.data[self._dict("stock_dates", number=i)[0], 2] = 0

        for i in range(self.max_stock_visible):
            if i < len(self.simulation.retrievals_in_parking):
                vehicle = self.simulation.retrievals_in_parking[-i-1]
                retrieval_in_sec = (vehicle.retrieval - self.simulation.t).total_seconds()
                self.data[self._dict("stock_dates", number=i)[0], 3] = retrieval_in_sec
                if vehicle.id in self.simulation.parking.occupation:
                    block_id, lane_id, position = self.simulation.parking.occupation[vehicle.id]
                    self.data[self._dict("stock_dates", number=i)[0], 4] = self.simulation.parking.to_global_id[(block_id, lane_id)]
                    self.data[self._dict("stock_dates", number=i)[0], 5] = position
                else:
                    self.data[self._dict("stock_dates", number=i)[0], 4] = 0
                    self.data[self._dict("stock_dates", number=i)[0], 5] = 0                  
                self.data[self._dict("stock_dates", number=i)[0], 6] = 1
            else:
                self.data[self._dict("stock_dates", number=i)[0], 6] = 0