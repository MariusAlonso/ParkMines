

class Simulation():
    def __init__(self, t0, stock):
        for v in stock.vehicles:
            if v.order_deposit < t0 :
                pass
        

class Vehicle():
    def __init__(self, id_vehicle, deposit, retrieval, order_deposit, order_retrieval):
        self.deposit = deposit
        self.retrieval = retrieval
        self.order_deposit = order_deposit
        self.order_retrieval = order_retrieval
        self.id = id_vehicle


class Stock():
    def __init__(self, vehicles) :
        self.vehicles = vehicles