import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import sys

from bank import Bank, Base

from decimal import Decimal, InvalidOperation
from datetime import datetime

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import logging

from exceptions import OverdrawError, TransactionLimitError, TransactionSequenceError

logging.basicConfig(filename='bank.log', level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class BankGUI:
    """Display a menu and respond to choices when run."""

    def __init__(self):
        ## intialize the database
        self._session = Session()
        self._bank = self._session.query(Bank).first()
        if not self._bank:
            self._bank = Bank()
            self._session.add(self._bank)
            self._session.commit()
        else:
            logging.debug("Loaded from bank.db")

        self._selected_account = None

        ## Create a window
        self._window = tk.Tk()
        self._window.geometry("400x300")
        self._window.configure(background="white")
        self._window.title("BANK")
        self._window.report_callback_exception = handle_exception
        
        self._options_frame = tk.Frame(self._window)

        self._current_account_label = tk.Label(self._options_frame, text=f"Currently selected account: {self._selected_account}")
        self._current_account_label.grid(row=0, column=1, columnspan=3)

        ## Buttons for options
        tk.Button(self._options_frame,
                  text="Open Account",
                  command=self._open_account).grid(row=1, column=1)
        tk.Button(self._options_frame,
                  text="Add Transaction",
                  command=self._add_transaction).grid(row=1, column=2)
        tk.Button(self._options_frame,
                  text="Interest and Fees",
                  command=self._interests_and_fees).grid(row=1, column=3)

        self._list_frame = tk.Frame(self._window)
        self._options_frame.grid(row=0, column=1, columnspan=2)
        self._list_frame.grid(row=2, column=1, columnspan=1, sticky="w")

        ## Initialize accounts_frame under the options_frame
        self._accounts_frame = tk.Frame(self._options_frame)
        self._accounts_frame.grid(row=1, column=1, columnspan=3)

        ## Listbox for accounts
        self._accounts_listbox = tk.Listbox(self._options_frame, bg="white")
        self._accounts_listbox.grid(row=3, column=1, columnspan= 3, sticky="nsew", padx=10, pady=(20, 10))
        self._accounts_listbox.bind('<<ListboxSelect>>', self._on_account_select)

        self._show_accounts()
        self._window.mainloop()

    def _open_account(self):
        """
        Open a new account.
        Gives a popup to open an account: choose between checking and savings, Save, and Cancel
        """
    
        ## Create a popup window
        self.popup = tk.Toplevel()
        self.popup.title("Open New Account")

        self.popup.geometry("200x100")
        self.popup.grab_set()

        # Label
        tk.Label(self.popup, text="Select Account Type:").pack()

        # Radio buttons for account type selection
        self.account_type = tk.StringVar()
        self.account_type.set("checking")  # set the default value
        tk.Radiobutton(self.popup, text="Checking", variable=self.account_type, value="checking").pack()
        tk.Radiobutton(self.popup, text="Savings", variable=self.account_type, value="savings").pack()

        # Enter button
        tk.Button(self.popup, text="Enter", command=lambda: self._confirm_account_creation(self.account_type.get())).pack(side=tk.LEFT)

        # Cancel button
        tk.Button(self.popup, text="Cancel", command=self.popup.destroy).pack(side=tk.RIGHT)

    def _confirm_account_creation(self, account_type):
        """Create a new account and save it to the database."""

        ## Create the account
        self._bank.add_account(account_type, self._session)
        self._session.commit()
        logging.debug("Saved to bank.db")
        messagebox.showinfo("Account Created", f"New {account_type} account created.")

        ## Update the listbox
        self._show_accounts()

    def _show_accounts(self):
        """Display the accounts in the listbox."""

        # Clear current items
        self._accounts_listbox.delete(0, tk.END)
        # Display Accounts
        accounts = self._bank.show_accounts()
        for account in accounts:
            self._accounts_listbox.insert(tk.END, account)

    def _on_account_select(self, event):
        """When an account is selected, update the label and ask if to show the transactions."""
        ## Get the selected account
        self._selected_account = self._accounts_listbox.get(tk.ACTIVE)

        ## update the label
        index = self._accounts_listbox.curselection()[0]
        self._selected_account = self._bank._accounts[index]
        self._current_account_label.config(text=f"Currently selected account: {self._selected_account._account_number}")
        
        ## Ask user if they want to see transactins
        popup = tk.Toplevel(self._window)
        popup.title("View Transactions")
        tk.Label(popup, text="Do you want to see the transactions?").pack(pady=10)

        ## Yes and No buttons
        tk.Button(popup, text="Yes", command=lambda: [self._review_transactions(), popup.destroy()]).pack(side=tk.LEFT, padx=(20, 10), pady=10)
        tk.Button(popup, text="No", command=popup.destroy).pack(side=tk.RIGHT, padx=(10, 20), pady=10)

    def _review_transactions(self):
        """Show the transactions of the selected account."""

        ## Create a popup window
        self.popup = tk.Toplevel()
        self.popup.title(f"{self._selected_account}")
        self.popup.geometry("400x200")
        self.popup.grab_set()

        ## if no transactions, print it
        if not self._selected_account.get_transactions():
            tk.Label(self.popup, text="No transactions found.").pack()
            return
        
        ## Print transactions from latest to oldest
        for t in self._selected_account.get_transactions()[::-1]:
            # if amount is negative, shown in red, else in green
            if t._amt < 0:
                tk.Label(self.popup, text=t, fg="red").pack()
            else:
                tk.Label(self.popup, text=t, fg="green").pack()

    def _add_transaction(self):
        """
        Add a transaction to the selected account
        Gives a popup to add a transaction: choose amount and date, Save, and Cancel
        """

        ## Check if an account is selected
        if not self._selected_account:
            messagebox.showerror("Please select an account first.", message="This command requires that you first select an account.")
            return

        ## Create a popup window
        self.popup = tk.Toplevel()
        self.popup.title("Add Transaction")
        self.popup.geometry("200x150")
        self.popup.grab_set()

        ## Label and Entry for amount
        tk.Label(self.popup, text="Amount:").pack()
        self.amount = tk.Entry(self.popup)
        self.amount.pack()

        ## Using a date picker
        tk.Label(self.popup, text="Date: (mm/dd/yy)").pack()
        self.date = DateEntry(self.popup, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date.pack()

        ## Enter button
        tk.Button(self.popup, text="Enter", command=self._confirm_transaction).pack(side=tk.LEFT)

        ## Cancel button
        tk.Button(self.popup, text="Cancel", command=self.popup.destroy).pack(side=tk.RIGHT)

    def _confirm_transaction(self):
        """Add a transaction to the selected account and save it to the database."""

        ## Get the amount and date handling exceptions
        try:
            amount = Decimal(self.amount.get())
        except InvalidOperation:
            messagebox.showerror("Please try again with a valid dollar amount.", message="Please try again with a valid dollar amount.")
            return

        try:
            date = self.date.get()
            date = datetime.strptime(date, "%m/%d/%y").date()
        except ValueError:
            messagebox.showerror("Please try again with a valid date in the format YYYY-MM-DD.", message="Please try again with a valid date in the format YYYY-MM-DD.")

        ## Add the transaction to the account
        try:
            self._selected_account.add_transaction(amount, date, self._session)
            self._session.commit()
            logging.debug("Saved to bank.db")
            ## Distroy the popup
            self.popup.destroy()
            ## Update the listbox and label and show the transactions
            self._show_accounts()
        except OverdrawError:
            messagebox.showerror("Insufficient account balance.", message="This transaction could not be completed due to an insufficient account balance.")
        except TransactionLimitError as ex:
            messagebox.showerror("Transaction Limit Error", message=f"This transaction could not be completed because this account already has {ex.limit} transactions in this {ex.limit_type}.")
        except TransactionSequenceError as ex:
            messagebox.showerror("Transaction Sequence Error", message=f"New transactions must be from {ex.latest_date} onward.")

        
        
    def _interests_and_fees(self):
        """Apply interest and fees to the selected account and save it to the database."""
        try:
            self._selected_account.assess_interest_and_fees(self._session)
            self._show_accounts()
            logging.debug("Triggered interest and fees")
            logging.debug("Saved to bank.db")
        except AttributeError:
            messagebox.showerror("Please select an account first.", message="This command requires that you first select an account.")
        except TransactionSequenceError as e:
            messagebox.showerror("Transaction Sequence Error", message=f"Cannot apply interest and fees again in the month of {e.latest_date.strftime('%B')}.")

def handle_exception(exception, value, traceback):
    print("Sorry! Something unexpected happened. If this problem persists please contact our support team for assistance.")
    logging.error(f"{exception.__name__}: {repr(value)}")
    sys.exit(0)

if __name__ == "__main__":
    engine = sqlalchemy.create_engine("sqlite:///bank.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    BankGUI()


