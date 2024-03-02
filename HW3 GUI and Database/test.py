import tkinter as tk
import tkinter.ttk as ttk
import tkcalendar as tkc

def main():
    root = tk.Tk()

    test_frame = ttk.Frame(root)
    test_frame.pack(side='top', fill='both', expand=True)

    test_date_entry = tkc.DateEntry(test_frame)
    test_date_entry.pack()

    root.mainloop()

if __name__ == '__main__':
    main()