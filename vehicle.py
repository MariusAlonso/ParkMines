         

class Vehicle():
    next_id = 1
    def __init__(self, deposit, retrieval, order_deposit, order_retrieval):
        self.deposit = deposit
        self.retrieval = retrieval
        self.order_deposit = order_deposit
        self.order_retrieval = order_retrieval
        self.id = self.__class__.next_id
        self.__class__.next_id += 1