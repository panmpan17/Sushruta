import os

from psd_tools import PSDImage


class PSDSplitter:
    def __init__(self, file_name, detination_folder):
        self.file_name = file_name
        self.psd = None

        self.export_images = []
        self.detination_folder = detination_folder
    
    def start(self):
        self.psd = PSDImage.load(self.file_name)

        for layer in self.psd.layers:
            image = layer.as_PIL()
            image.save(os.path.join(self.detination_folder, layer.name + ".png"))


if __name__ == "__main__":
    splitter = PSDSplitter("/Users/michael/Loneliness/美術/場景意象圖/辦公室.psd", "result")
    splitter.start()
