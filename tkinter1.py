from tkinter import *
from tkinter import ttk

window = Tk()
window.title("Hello World")


def handle_button_press(event):
    print("The button was pressed.")


button = ttk.Button(text="My simple app.")
button.bind("<Button-1>", handle_button_press)
button.pack()

# Start the event loop.
window.mainloop()
