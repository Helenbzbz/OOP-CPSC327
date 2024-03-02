import tkinter as tk
from cli import BankCLI

class BankGUI:
    """Display a menu and respond to choices when run."""

    def __init__(self):

        self._window = tk.Tk()
        self._window.title("BANK")

        self._bank = BankCLI()
        self._options_frame = tk.Frame(self._window)

        tk.Button(self._options_frame,
                  text="Create Account",
                #   command=self._search_notes
                ).grid(row=1, column=1)
        # tk.Button(self._options_frame,
        #           text="Add Note",
        #           command=self._add_note).grid(row=1, column=2)
        # tk.Button(self._options_frame,
        #           text="Save",
        #           command=self._save).grid(row=1, column=3)
        # tk.Button(self._options_frame,
        #           text="Load",
        #           command=self._load).grid(row=1, column=4)

        self._list_frame = tk.Frame(self._window)
        self._options_frame.grid(row=0, column=1, columnspan=2)
        self._list_frame.grid(row=2, column=1, columnspan=1, sticky="w")

        self._window.mainloop()

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

    # def _load(self):
    #     with open("notebook_save.pickle", "rb") as f:
    #         self._notebook = pickle.load(f)

    #     notes = self._notebook.all_notes()

    #     self._list_frame.destroy()
    #     self._list_frame = tk.Frame(self._window)
    #     self._list_frame.grid(row=2, column=1, columnspan=1, sticky="w")
    #     for n in notes:
    #         NoteButton(self._list_frame, n).pack()


if __name__ == "__main__":
    BankGUI()


