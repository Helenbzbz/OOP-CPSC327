import logging
from decimal import Decimal

from transactions import Transaction, Base
from exceptions import TransactionSequenceError, OverdrawError, TransactionLimitError

from sqlalchemy import Column, Integer, create_engine, ForeignKey, String
from sqlalchemy.orm import relationship, backref


class Account(Base):
    """This is an abstract class for accounts.  Provides default functionality for adding transactions, getting balances, and assessing interest and fees.  
    Accounts should be instantiated as SavingsAccounts or CheckingAccounts
    """

    ## Initialize SQLAlchemy table
    __tablename__ = 'accounts'

    _id = Column(Integer, primary_key=True)
    _account_number = Column(Integer)
    _transactions = relationship("Transaction", backref=backref("accounts"))

    _type = Column(String)
    __mapper_args__ = {
        'polymorphic_identity': 'account',
        'polymorphic_on': _type,
    }

    _bank_id = Column(Integer, ForeignKey("banks._id"))
    
    def __init__(self, acct_num, type):
        self._account_number = acct_num
        self._type = type
        logging.debug(f"Created account: {self._account_number}")

    def _get_acct_num(self):
        return self._account_number

    account_number = property(_get_acct_num)

    def add_transaction(self, amt, date, session, exempt=False):
        """Creates a new transaction and checks to see if it is allowed, adding it to the account if it is.

        Args:
            amt (Decimal): amount for new transaction
            date (Date): Date for the new transaction.
            exempt (bool, optional): Determines whether the transaction is exempt from account limits. Defaults to False.
        """

        t = Transaction(amt,
                        self._account_number,
                        date=date, 
                        exempt=exempt)

        if not t.is_exempt():
            self._check_balance(t)
            self._check_limits(t)
            self._check_date(t)
        self._transactions.append(t)

        session.add(t)
        session.commit()

    def _check_balance(self, t):
        """Checks whether an incoming transaction would overdraw the account

        Args:
            t (Transaction): pending transaction

        Returns:
            bool: false if account is overdrawn
        """
        if not t.check_balance(self.get_balance()):
            raise OverdrawError()

    def _check_limits(self, t):
        pass

    def _check_date(self, t):
        if len(self._transactions) > 0:
            latest_transaction = max(self._transactions)
            if t < latest_transaction:
                raise TransactionSequenceError(latest_transaction.date)

    def get_balance(self):
        """Gets the balance for an account by summing its transactions

        Returns:
            Decimal: current balance
        """
        # could have a balance variable updated when transactions are added (or removed) which is faster
        # but this is more foolproof since it's always in sync with transactions
        # this could be improved by caching the sum to avoid too much
        # recalculation, while still maintaining the list as the ground truth
        return sum(self._transactions)

    def _assess_interest(self, latest_transaction, session):
        """Calculates interest for an account balance and adds it as a new transaction exempt from limits.
        """
        if self._type == 'checking':
            interest_rate = Decimal("0.0008")
        else:
            interest_rate = Decimal("0.0041")
        self.add_transaction(self.get_balance() * interest_rate, 
                        date=latest_transaction.last_day_of_month(), 
                        session = session,
                        exempt=True)

    def _assess_fees(self, latest_transaction, session):
        pass

    def assess_interest_and_fees(self, session):
        """Used to apply interest and/or fees for this account

        Raises:
            TransactionSequenceError: Indicates that the new transactions were
            not newer than the most recent interest or fees transactions
        """
        latest_transaction = max(self._transactions)
        for t in self._transactions:
            if t.is_exempt() and t.in_same_month(latest_transaction):
                # found an interest or fee transaction that is already in the
                # same month as the most recent transaction
                raise TransactionSequenceError(t.date)
        self._assess_interest(latest_transaction, session)
        self._assess_fees(latest_transaction, session)

    def __str__(self):
        """Formats the account number and balance of the account.
        For example, '#000000001,<tab>balance: $50.00'
        """
        return f"#{self._account_number:09},\tbalance: ${self.get_balance():,.2f}"

    def get_transactions(self):
        "Returns sorted list of transactions on this account"
        return sorted(self._transactions)


class SavingsAccount(Account):
    """Concrete Account class with daily and monthly account limits and high interest rate.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'savings',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _check_limits(self, t1):
        """determines if the incoming trasaction is within the accounts transaction limits

        Args:
            t1 (Transaction): pending transaction to be checked

        Returns:
            bool: true if within limits and false if beyond limits
        """
        # Count number of non-exempt transactions on the same day as t1
        num_today = len(
            [t2 for t2 in self._transactions if not t2.is_exempt() and t2.in_same_day(t1)])
        # Count number of non-exempt transactions in the same month as t1
        num_this_month = len(
            [t2 for t2 in self._transactions if not t2.is_exempt() and t2.in_same_month(t1)])
        # check counts against daily and monthly limits
        if num_today >= 2:
            raise TransactionLimitError("day", 2)
        if num_this_month >= 5:
            raise TransactionLimitError("month", 5)

    def __str__(self):
        """Formats the type, account number, and balance of the account.
        For example, 'Savings#000000001,<tab>balance: $50.00'
        """
        return "Savings" + super().__str__()


class CheckingAccount(Account):
    """Concrete Account class with lower interest rate and low balance fees.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'checking',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _assess_fees(self, latest_transaction, session):
        """Adds a low balance fee if balance is below a particular threshold. Fee amount and balance threshold are defined on the CheckingAccount.
        """
        if self.get_balance() < 100:
            self.add_transaction(Decimal("-5.44"),
                                 date=latest_transaction.last_day_of_month(), 
                                 session=session,
                                 exempt=True)

    def __str__(self):
        """Formats the type, account number, and balance of the account.
        For example, 'Checking#000000001,<tab>balance: $50.00'
        """
        return "Checking" + super().__str__()

if __name__ == "__main__":
    # if the db file already exists, this does nothing
    engine = create_engine(f"sqlite:///notebook.db")
    Base.metadata.create_all(engine)
