from tkinter import Button as TkButton, Tk

from Pin import Pin

class Output(Pin):
    def __init__(self, master=None, image=None, **kw):
        self.image = image
        super().__init__(master, image=self.image, **kw)