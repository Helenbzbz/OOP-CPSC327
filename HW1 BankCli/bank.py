from account import SavingsAccount, CheckingAccount

class Bank():
    """This class is a Bank that stores a dict of accounts, with account id as the key and account object as the value. 
    It includes methods to:
    1. Open a new account
    2. Summarize all accounts
    3. Select an account by id"""

    def __init__(self, accounts = {}):
        """Initialize a bank with a dict of accounts"""
        self._accounts = accounts

    def open_account(self, type):
        """Open a new account based on the type of account"""
        if type == 'checking':
            account = CheckingAccount()
        elif type == 'savings':
            account = SavingsAccount()
        self._accounts[account.id] = account
        
    def summary(self):
        """Summarize all accounts print their balance, account type, and account_id"""
        for account_id, account in self._accounts.items():
            account_title = f'{account.type}#{str(account_id).zfill(9)}'
            print(f'{account_title},\tbalance: ${round(account.balance, 2)}')

    def select_account(self, account_id):
        """Select an account by id"""
        return self._accounts[account_id]
    