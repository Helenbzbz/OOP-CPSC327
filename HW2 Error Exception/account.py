from datetime import timedelta
import datetime
from decimal import Decimal
from transaction import Transaction
import logging

logger = logging.getLogger('bank_application')

## Define 3 exceptions -- OverdrawError, TransactionSequenceError, TransactionLimitError
class OverdrawError(Exception):
    """Exception raised for attempts to overdraw an account."""
    def __init__(self):
        pass

class TransactionSequenceError(Exception):
    """Exception raised for adding transactions out of chronological order; Or duplicate interest and fee transactions."""
    def __init__(self):
        pass

class TransactionLimitError(Exception):
    """Exception raised for exceeding transaction limits on SavingsAccounts."""
    def __init__(self, limit_type):
        self._limit_type = limit_type
        if limit_type == "daily":
            self.message = "This transaction could not be completed because this account already has 2 transactions in this day."
        if limit_type == "monthly":
            self.message = "This transaction could not be completed because this account already has 5 transactions in this month."
        super().__init__(self.message)

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

    def __init__(self):
        """initialize a note with memo and optional
        space-separated tags. Automatically set the note's
        creation date and a unique id."""

        self.balance =  Decimal(0)
        self._transactions = []
        self.latest_transaction_date = None

        Account.last_id += 1
        self.id = Account.last_id

    def transaction_record(self, amount, type, date):
        """Add a transaction with the amount and date to the list of transactions, sorted by date"""
        
        ## Handle Transaction Sequence Error
        if self.latest_transaction_date and date < self.latest_transaction_date:
            raise TransactionSequenceError
        
        new_transaction = Transaction(amount, type, date)
        self._transactions.append(new_transaction)
        self._transactions.sort(key=lambda x: x.date)
        self.latest_transaction_date = date
        self.balance += amount

        logger.debug(f"Created transaction: {self.id}, {amount:,.6f}")

    def list_transactions(self):
        """List all transactions"""
        for transaction in self._transactions:
            print(f'{transaction.date}, ${transaction.amount:,.2f}')

    def check_balance_limit(self, amount):
        """Check if a new transaction will violate the balance limit"""
        if self.balance + amount < 0:
            return False
        return True

    def interest_and_fee_base(self, interest_rate):
        """Add a transaction to the list of transactions with the interest: total_balance * monthly interest rate
        Add a fee: $5.44 if balance is less than 100"""

        ## if no transaction has been made, return
        if not self.latest_transaction_date:
            return

        ## Deal with inetrest
        interest = self.balance * interest_rate

        ## Find the last day of the month of latest transaction
        next_month = self.latest_transaction_date.replace(day=28) + timedelta(days=4) 
        latest_month_end = next_month - timedelta(days=next_month.day)

        ## Test for Transaction Sequence Error
        for transaction in self._transactions:
            if transaction.date == latest_month_end and transaction.type == 0:
                raise TransactionSequenceError

        ## Adjsut the interest to the last day of the month of latest transaction
        self.transaction_record(interest, 0, latest_month_end)

        ## Deal with fee
        if self.balance < 100:
            self.transaction_record(Decimal(-5.44),0, latest_month_end)

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

    def add_transaction(self, amount, date):
        """Add a transaction to the list of transactions if it does not violate the balance limit"""
        if self.check_balance_limit(amount):
            self.transaction_record(amount, 1, date)
        else:
            raise OverdrawError

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
            if transaction.date == date and transaction.type == 1:
                day_count += 1
            if transaction.date.month == date.month and transaction.type == 1:
                month_count += 1
            if day_count >= 2:
                raise TransactionLimitError("daily")
            if month_count >= 5:
                raise TransactionLimitError("monthly")
        return True

    def add_transaction(self, amount, date):
        """Add a transaction to the list of transactions if it does not violate the balance limit and if it does not violate the frequency limit"""
        if not self.check_balance_limit(amount):
            raise OverdrawError
        if self.check_frequency_limit(date):
            self.transaction_record(amount, 1, date)
