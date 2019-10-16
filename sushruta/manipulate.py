import os

from PIL import Image


class Manipulator:
    def clamp(num, _min, _max):
        if num < _min:
            return _min
        elif num > _max:
            return _max
        return num

    @classmethod
    def get_img_name(cls, file_path):
        return ".".join(file_path.split("/")[-1].split(".")[:-1])

    @classmethod
    def tune_multiplier(cls, file_path, tune_multiplier, result_folder=""):
        try:
            img = Image.open(file_path)
        except FileNotFoundError:
            return "File not exist"

        file_name = cls.get_img_name(file_path)

        for x in range(img.width):
            for y in range(img.height):
                color = list(img.getpixel((x, y)))
                for i, value in enumerate(color):
                    if i < len(tune_multiplier):
                        color[i] = cls.clamp(
                            int(color[i] * tune_multiplier[i]), 0, 255)

                img.putpixel((x, y), tuple(color))

        img.save(os.path.join(result_folder, f"{file_name}.png"), "PNG")
        img.close()
