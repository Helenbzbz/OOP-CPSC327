from datetime import timedelta
import datetime
from decimal import Decimal

class Account():
    """
    Represent an Account in the Bank. This is the parent class for  Checking and Savings accounts.
    Stores list of transactions, balance, and latest transaction date.
    Includes methods to: 
    1. add transaction to lists of transactions
    2. List all transactions
    3. Check if a new transaction will violate the balance limit
    4. Interest and fee: Add a transaction to the list of transactions with the interest: total_balance * monthly interest rate; Add fee if balance is less than 100
    """

    # Store the next available id for all new notes
    last_id = 0

    def __init__(self, balance = Decimal(0), transactions = [], latest_transaction_date = None):
        """initialize a note with memo and optional
        space-separated tags. Automatically set the note's
        creation date and a unique id."""

        self.balance = balance
        self._transactions = transactions
        self._latest_transaction_date = latest_transaction_date

        Account.last_id += 1
        self.id = Account.last_id

    def transaction_record(self, amount, date):
        """Add a transaction with the amount and date to the list of transactions, sorted by date"""
        self._transactions.append((amount, date))
        self._transactions.sort(key=lambda x: x[1])

        if not self._latest_transaction_date:
            self._latest_transaction_date = date
        else:
            self._latest_transaction_date = max(self._latest_transaction_date, date)

        self.balance += amount

    def list_transactions(self):
        """List all transactions"""
        for transaction in self._transactions:
            print(f'{transaction[1]}, ${transaction[0]:,.2f}')

    def check_balance_limit(self, amount):
        """Check if a new transaction will violate the balance limit"""
        if self.balance + amount < 0:
            return False
        return True

    def interest_and_fee_base(self, interest_rate):
        """Add a transaction to the list of transactions with the interest: total_balance * monthly interest rate
        Add a fee: $5.44 if balance is less than 100"""

        ## Deal with inetrest
        interest = self.balance * interest_rate

        ## Find the last day of the month of latest transaction
        next_month = self._latest_transaction_date.replace(day=28) + timedelta(days=4) 
        latest_month_end = next_month - timedelta(days=next_month.day)

        ## Adjsut the interest to the last day of the month of latest transaction
        self.transaction_record(interest, latest_month_end)
        self.balance += interest

        ## Deal with fee
        if self.balance < 100:
            self.transaction_record(Decimal(-5.44), latest_month_end)

class CheckingAccount(Account):
    """This is a Checking Account. It is a child class of Account.
    It has 2 methods defined further than parent class:
    1. add_transaction: Add a transaction to the list of transactions if it does not violate the balance limit
    2. interest_and_fee: with interest rate of 0.08% and fee of $5.44"""
    def __init__(self):
        super().__init__()
        self.type = 'Checking'

    def interest_and_fee(self):
        """Call the interest_and_fee_base method with interest rate of 0.08% and fee of $5.44"""
        self.interest_and_fee_base(Decimal(0.0008))

    def add_transaction(self, date, amount):
        """Add a transaction to the list of transactions if it does not violate the balance limit"""
        if self.check_balance_limit(amount):
            self.transaction_record(amount, date)

class SavingsAccount(Account):
    """This is a Savings Account. It is a child class of Account.
    It has 2 methods defined further than parent class:
    1. add_transaction: Add a transaction to the list of transactions if it does not violate the balance limit and if it does not violate the frequency limit
    2. interest_and_fee: with interest rate of 0.41% and fee of $5.44"""

    def __init__(self):
        super().__init__()
        self.type = 'Savings'

    def interest_and_fee(self):
        """Call the interest_and_fee_base method with interest rate of 0.41% and fee of $5.44"""
        self.interest_and_fee_base(Decimal(0.0041))

    def check_frequency_limit(self, date):
        """Check if a new transaction will violate the frequency limit, daily limit = 2, monthly limit = 5"""
        day_count, month_count = 0, 0
        for transaction in self._transactions:
            if transaction[1] == date:
                day_count += 1
            if transaction[1].month == date.month:
                month_count += 1
            if day_count >= 2 or month_count >= 5:
                return False
        return True

    def add_transaction(self, date, amount):
        """Add a transaction to the list of transactions if it does not violate the balance limit and if it does not violate the frequency limit"""
        if self.check_balance_limit(amount) and self.check_frequency_limit(date):
            self.transaction_record(amount, date)

