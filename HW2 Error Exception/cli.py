import sys
import pickle
import logging
from bank import Bank
from datetime import datetime
from decimal import Decimal, InvalidOperation
from account import TransactionSequenceError, OverdrawError, TransactionLimitError

class BankCli():
    """Display a menu and respond to choices when run."""

    def __init__(self):
        self._bank = Bank()
        self.current_account = None
        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select_account,
            "4": self._add_transaction,
            "5": self._list_transactions,
            "6": self._interest_and_fee,
            "7": self._save,
            "8": self._load,
            "9": self._quit
        }

    def _display_menu(self):
        if self.current_account == None:
            text_for_account = 'None'
        else:
            text_for_account = f'{self.current_account.type}#{str(self.current_account.id).zfill(9)},\tbalance: ${round(self.current_account.balance, 2)}'
        print("--------------------------------")
        print(f"Currently selected account: {text_for_account}")
        print("Enter command\n"
        "1: open account\n"
        "2: summary\n"
        "3: select account\n"
        "4: add transaction\n"
        "5: list transactions\n"
        "6: interest and fees\n"
        "7: save\n"
        "8: load\n"
        "9: quit")

    def run(self):
        """Display the menu and respond to choices."""
        while True:
            self._display_menu()
            choice = input(">")
            action = self._choices.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))

    def _open_account(self):
        type = input("Type of account? (checking/savings)\n>")
        self._bank.open_account(type)

    def _summary(self):
        self._bank.summary()

    def _select_account(self):
        account_id = input("Enter account number\n>")
        self.current_account = self._bank.select_account(int(account_id))

    def _add_transaction(self):
        ## Handle invalid dollar amount error and re-prompt
        valid_amount = False
        while not valid_amount:
            try:
                amount = Decimal(input("Amount?\n>"))
                valid_amount = True
            except InvalidOperation or ValueError:
                print("Please try again with a valid dollar amount.")
        
        ## Handle invalid date error and re-prompt
        valid_date = False
        while not valid_date:
            try:
                date_input = input("Date? (YYYY-MM-DD)\n>")
                date = datetime.strptime(date_input, "%Y-%m-%d").date()
                valid_date = True
            except ValueError:
                print("Please try again with a valid date in the format YYYY-MM-DD.")

        ## Handle account not selected error
        try:
            self.current_account.add_transaction(amount, date)
        except AttributeError:
            print('This command requires that you first select an account.')
        except OverdrawError:
            print('This transaction could not be completed due to an insufficient account balance.')
        except TransactionLimitError as e:
            print(e.message)
        except TransactionSequenceError:
            print('New transactions must be from {} onward.'.format(self.current_account._latest_transaction_date.strftime("%Y-%m-%d")))

    def _list_transactions(self):
        ## Handle account not selected error
        try:
            self.current_account.list_transactions()
        except AttributeError:
            print('This command requires that you first select an account.')

    def _interest_and_fee(self):
        ## Handle account not selected error
        try:
            self.current_account.interest_and_fee()
        except AttributeError:
            print('This command requires that you first select an account.')
        except TransactionSequenceError:
            print("Cannot apply interest and fees again in the month of {}.".format(self._latest_transaction_date.strftime("%B")))
                
    def _save(self):
        with open("bank_save.pickle", "wb") as f:
            pickle.dump(self._bank, f)

    def _load(self):
        with open("bank_save.pickle", "rb") as f:   
            self._bank = pickle.load(f)

    def _quit(self):
        sys.exit(0)

if __name__ == "__main__":
    try: 
        BankCli().run()
    except Exception as e:
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        exception_message = repr(e)  
        logging.error(f"{e.__class__.__name__}: {exception_message}")
        sys.exit(1)