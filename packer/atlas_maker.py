import logging
import os

from PIL import Image, ImageChops
from psd_tools import PSDImage


def print_danger(text):
    """
    Print red text
    """

    print("\033[0;31m" + text + "\x1b[0m")


def trim_img(image):
    bg = Image.new(image.mode, image.size, (0, 0, 0, 0))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)

    bbox = diff.getbbox()
    if bbox:
        bg.close()
        return image.crop(bbox)
    return None


class ImageSource:
    def __init__(self, file_path=""):
        self.file_name = file_path[file_path.rfind("/") + 1:]
        self.file_path = file_path

        self.file = None
        self.loaded = False

        self.width = 0
        self.height = 0

    def load(self, trim=True):
        img = Image.open(self.file_path)

        if trim:
            self.file = trim_img(img)
            img.close()
        else:
            self.file = img

        self.width = self.file.width
        self.height = self.file.height

        self.loaded = True

    def assign_image(self, img, trimming=True):
        if trimming:
            self.file = trim_img(img)
        else:
            self.file = img

        self.width = self.file.width
        self.height = self.file.height

        self.loaded = True

    def close(self):
        self.file.close()


class PSDSouce:
    def __init__(self, file_path, trimming=True):
        self.file_name = file_path[file_path.rfind("/") + 1:]
        self.file_path = file_path
        self.trimming = trimming

        self.images = []

    def load(self):
        psd_file = PSDImage.load(self.file_path)

        self.scan_layer(psd_file.layers)

    def scan_layer(self, layers):
        for i, layer in enumerate(layers):
            if layer.is_group():
                self.scan_layer(layer.layers)
            else:
                pil_img = layer.as_PIL()
                if pil_img is None:
                    continue

                path = self.file_path + str(i)
                image = ImageSource(path)
                image.assign_image(pil_img, trimming=self.trimming)

                pil_img.close()

                self.images.append(image)


class Atlas:
    def __init__(self, max_size=2048, padding=2):
        self.max_size = max_size
        self.padding = padding

        self.images = {}
        self.images_name = {}

        self.boxes = [(0, 0, max_size, max_size)]

    def __repr__(self):
        txt = f"{self.max_size} x {self.max_size}\n"

        for img in self.images.values():
            txt += (f"{img['source'].file_name} - {img['left']}, "
                    f"{img['top']}, {img['right']}, {img['bottom']}\n")
        return txt + "\n"

    def find_boxes(self):
        """
        Find all the boxes in atlas
        """

        self.boxes.clear()

        for img in self.images.values():
            # Find the point using img top-right and bottom-left corner.
            self.find_box(img["right"], img["top"])
            self.find_box(img["left"], img["bottom"])

    def find_box(self, x, y):
        """
        Find empty box which image wil be placed in from certain pos.
        x, y (int)
        """

        # Box boundary initial.
        left = x
        top = 0
        right = self.max_size - 1
        bottom = self.max_size - 1

        for img in self.images.values():
            # Is x inline with other image?
            if img["left"] <= x < img["right"]:
                if img["top"] <= y < img["bottom"]:
                    # If y also inline other image -> no box place. End.
                    return

                elif img["bottom"] <= y and top < img["bottom"]:
                    # If img is on top of the point then change top.

                    top = img["bottom"]

                elif img["top"] > y and bottom > img["top"]:
                    # If img is below the point then change bottom.

                    bottom = img["top"]

        for img in self.images.values():
            if (img["top"] <= top < img["bottom"]) or\
                    (img["top"] <= bottom < img["bottom"]):
                # if box top or bottom contact with img.

                if right > img["left"] and left < img["left"]:
                    # If img is on the right side then change right.

                    right = img["left"]

        self.boxes.append((left, top, right, bottom))

    def add_image(self, new_img):
        """
        Place image in the box
        """

        smallest_box_index = None
        smallest_box = None
        for i, box in enumerate(self.boxes):
            box_width = box[2] - box[0]
            box_height = box[3] - box[1]
            if new_img.width <= box_width and new_img.height <= box_height:
                # Check is box size big enough for new_img

                if smallest_box is not None:
                    if smallest_box <= box_width * box_height:
                        continue

                smallest_box_index = i
                smallest_box = box_width * box_height

        if smallest_box_index is not None:
            name = new_img.file_name
            if name not in self.images_name:
                self.images_name[name] = 1
            else:
                self.images_name[name] += 1
                name = name.replace(
                    ".", "_" + str(self.images_name[name]) + ".")

            box = self.boxes[smallest_box_index]
            self.images[name] = {
                "left": box[0],
                "top": box[1],
                "right": box[0] + new_img.width + self.padding,
                "bottom": box[1] + new_img.height + self.padding,
                "source": new_img,
                "name": name}
            # new_img.place(box, self.padding)

            self.find_boxes()
            return True
        else:
            return False

    def save(self, file_name, trim=False):
        new_image = Image.new("RGBA", (self.max_size, self.max_size))

        for image in self.images.values():
            new_image.paste(image["source"].file,
                            box=(image["left"], image["top"]))
            image["source"].close()

        if trim:
            trimed_image = trim_img(new_image)
        else:
            rightmost_left = 0
            lowest_top = 0

            for box in self.boxes:
                if box[0] > rightmost_left:
                    rightmost_left = box[0]
                if box[1] > lowest_top:
                    lowest_top = box[1]

            trimed_image = new_image.crop((0, 0, rightmost_left, lowest_top))

        trimed_image.save(file_name)
        trimed_image.close()
        new_image.close()


class AtlasMaker:
    def __init__(self, max_size=2048, padding=2):
        self.max_size = max_size
        self.padding = padding

        self.atlases = []
        self.images = []
        self.unused_images = set()

    def add_images(self, *images, trim=True):
        for image in images:
            if type(image) == str:
                self.images.append(ImageSource(image))
                self.images[-1].load(trim)
            elif type(image) == ImageSource:
                if not image.loaded:
                    image.load(trim)

                self.images.append(image)

    def make(self):
        for image in self.images:
            placed = False

            if image.width > self.max_size or image.height > self.max_size:
                print_danger(f"{image.file_name} is too big")
                self.unused_images.add(image)

            for atlas in self.atlases:
                placed = atlas.add_image(image)
                if placed:
                    break
            else:
                atlas = Atlas(self.max_size, self.padding)
                if atlas.add_image(image):
                    self.atlases.append(atlas)
                else:
                    print_danger(f"Something wrong '{image.file_path}'")

    def save(self, result_folder="", prefix="", trim=True):
        for i, atlas in enumerate(self.atlases):
            try:
                atlas.save(os.path.join(result_folder, f"{prefix}{i}.png"), trim)
            except Exception:
                logging.exception(f"{prefix}{i}.png failed")
