import tkinter as tk
from tkinter import Button, Label
from bank import Bank, Base

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import logging

# from note_button import NoteButton
# from note_entry import NoteEntry
# from notebook import Notebook
# from search_popup import SearchPopup

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

        self._window = tk.Tk()
        self._window.geometry("400x300")
        self._window.configure(background="#00254a")
        self._window.title("BANK")

        self._bank = Bank()

        user_name = Label(self._window, 
                  text = "Username").place(x = 40,
                                           y = 60)  
         
        # btn1 = Button(self._window, text = 'Click me !', command = self._window.destroy).grid(padx=10, pady=10)
        # btn1.place(x=100, y=20)
        
        # self._show_accounts()

        # self._list_frame = tk.Frame(self._window, bg='light blue')
        # self._options_frame.grid(row=10, column=1, columnspan=2)
        # self._list_frame.grid(row=10, column=1, columnspan=1, sticky="w")

        self._window.mainloop()

    # def _open_account(self):
    #     pass

    # def _search_notes(self):
    #     SearchPopup(self._window, self._notebook)

    # def _add_note(self):
    #     def add_callback():
    #         n = self._notebook.new_note(e1.get())
    #         NoteButton(self._list_frame, n).pack()

    #         e1.destroy()
    #         b.destroy()
    #         l1.destroy()

    #     l1 = tk.Label(self._options_frame, text="Memo:")
    #     l1.grid(row=2, column=1)
    #     e1 = tk.Entry(self._options_frame)
    #     e1.grid(row=3, column=1)

    #     b = tk.Button(self._options_frame, text="Enter", command=add_callback)
    #     b.grid(row=3, column=2)

    # def _save(self):
    #     with open("notebook_save.pickle", "wb") as f:
    #         pickle.dump(self._notebook, f)

    # def _show_accounts(self):
    #     for x in self._bank.show_accounts():
    #         tk.Label(self._list_frame, text=x).pack()

if __name__ == "__main__":

    engine = sqlalchemy.create_engine("sqlite:///bank.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # try:
    #     BankCLI().run()
    # except Exception as e:
    #     print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
    #     logging.error(str(e.__class__.__name__) + ": " + repr(str(e)))

    BankGUI()