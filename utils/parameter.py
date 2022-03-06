import os


class Parameter:
    def __init__(self, words, version=1, level='H', picture=None, colorized=False, contrast=1.0, brightness=1.0,
                 name=None, save_dir=os.getcwd()):
        self.words = words
        self.version = version
        self.level = level
        self.picture = picture
        self.colorized = colorized
        self.contrast = contrast
        self.brightness = brightness
        self.name = name
        self.save_dir = save_dir

