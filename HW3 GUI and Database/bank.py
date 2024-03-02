from accounts import SavingsAccount, CheckingAccount, Base

from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import declarative_base, relationship, backref

SAVINGS = "savings"
CHECKING = "checking"

class Bank(Base):

    ## initilaize SQLAlchemy table
    __tablename__ = 'banks'
    _id = Column(Integer, primary_key=True)
    _accounts = relationship("Account", backref=backref("banks"))

    def add_account(self, acct_type, session):
        """Creates a new Account object and adds it to this bank object. The Account will be a SavingsAccount or CheckingAccount, depending on the type given.

        Args:
            type (string): "Savings" or "Checking" to indicate the type of account to create
        """
        acct_num = self._generate_account_number()
        if acct_type == SAVINGS:
            a = SavingsAccount(acct_num, acct_type)
        elif acct_type == CHECKING:
            a = CheckingAccount(acct_num, acct_type)
        else:
            return None
        self._accounts.append(a)
        session.add(a)
        session.commit()

    def _generate_account_number(self):
        return len(self._accounts) + 1

    def show_accounts(self):
        "Accessor method to return accounts"
        return self._accounts

    def get_account(self, account_num):
        """Fetches an account by its account number.

        Args:
            account_num (int): account number to search for

        Returns:
            Account: matching account or None if not found
        """        
        for x in self._accounts:
            if x.account_number == account_num:
                return x
        return None

if __name__ == "__main__":
    # if the db file already exists, this does nothing
    engine = create_engine(f"sqlite:///notebook.db")
    Base.metadata.create_all(engine)
