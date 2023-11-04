from PIL import Image

class LeftPanelButton:
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.image = self.get_image()
        
    def get_image(self):
        image = Image.open('Images/' + self.name + '.png')
        return image