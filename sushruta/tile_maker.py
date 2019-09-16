import os
import math
from PIL import Image


class ImageTile:
    @classmethod
    def tile_by_size(cls, file_name, width, height, result_folder=""):
        try:
            img = Image.open(file_name)
        except FileNotFoundError:
            return "File not exist"

        if img.width > width or img.height > height:
            print("Currently not support smaller size tileing")
            return

        new_img = Image.new(img.mode, (width, height))

        for x_count in range(math.ceil(width / img.width)):
            for y_count in range(math.ceil(height / img.height)):
                new_img.paste(img,
                              (x_count * img.width, y_count * img.height))

        name = ".".join(file_name.split("/")[-1].split(".")[:-1])
        new_img.save(os.path.join(result_folder,
                                  f"{name}-{width}-{height}.png"))

        img.close()
        new_img.close
