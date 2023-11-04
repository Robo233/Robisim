import tkinter as tk
from dragging import create_buttons

root = tk.Tk()
root.state('zoomed')
root.title("Robisim")

create_buttons(root)

root.mainloop()