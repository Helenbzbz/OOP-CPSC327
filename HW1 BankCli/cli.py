import sys
import pickle
from bank import Bank
from datetime import datetime
from decimal import Decimal

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
        amount = Decimal(input("Amount?\n>"))
        date_input = input("Date? (YYYY-MM-DD)\n>")
        date = datetime.strptime(date_input, "%Y-%m-%d").date()
        self.current_account.add_transaction(amount, date)

    def _list_transactions(self):
        self.current_account.list_transactions()

    def _interest_and_fee(self):
        self.current_account.interest_and_fee()

    def _save(self):
        with open("bank_save.pickle", "wb") as f:
            pickle.dump(self._bank, f)

    def _load(self):
        with open("bank_save.pickle", "rb") as f:   
            self._bank = pickle.load(f)

    def _quit(self):
        sys.exit(0)

if __name__ == "__main__":
    BankCli().run()