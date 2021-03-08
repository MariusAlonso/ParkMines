

class Simulation():
    def __init__(self, t0, stock):
        for v in stock.vehicles:
            if v.order_deposit < t0 :
                pass
        

class Vehicle():
    id = 0
    def __init__(self, deposit, retrieval, order_deposit, order_retrieval):
        self.deposit = deposit
        self.retrieval = retrieval
        self.order_deposit = order_deposit
        self.order_retrieval = order_retrieval
        id += 1
        self.id = id


class Stock():
    def __init__(self, vehicles) :
        self.vehicles = vehicles