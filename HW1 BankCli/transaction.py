class Transaction():
    """This is a Transaction class that stores: date, amount, type (1: user_initiated; 0: system_initiated)"""
    def __init__(self, amount, type, date):
        self.amount = amount
        self.type = type
        self.date = date
    