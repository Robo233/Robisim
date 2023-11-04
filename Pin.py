from tkinter import Button as TkButton, Tk

class Pin(TkButton):
    def __init__(self, master=None, image=None, **kw):
        self.image = image
        super().__init__(master, image=self.image, **kw)

    label = None