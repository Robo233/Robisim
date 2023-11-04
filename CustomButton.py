from tkinter import Button as TkButton, Tk

class CustomButton(TkButton):
    def __init__(self, master=None, image=None, category=None, **kw):
        self.category = category
        self.image = image
        super().__init__(master, image=self.image, **kw)