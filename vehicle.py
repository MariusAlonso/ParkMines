         

class Vehicle():
    next_id = 1
    def __init__(self, deposit, retrieval, order_deposit, order_retrieval):
        self.deposit = deposit
        self.retrieval = retrieval
        self.order_deposit = order_deposit
        self.order_retrieval = order_retrieval
        self.id = self.__class__.next_id
        self.__class__.next_id += 1
        if Vehicle.next_id >= 100000:
            raise ValueError("La représentation d'un block ne fonctionne que si les ids des véhicules contiennent au plus cinq chiffres")
    
    def __repr__(self):
        return self.id.__repr__()