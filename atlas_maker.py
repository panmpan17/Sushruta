import logging
from PIL import Image, ImageDraw, ImageChops


def print_danger(text):
    """
    Print red text
    """

    print("\033[0;31m" + text + "\x1b[0m")


def trim(image):
    bg = Image.new(image.mode, image.size, (0, 0, 0, 0))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)

    bbox = diff.getbbox()
    if bbox:
        bg.close()
        return image.crop(bbox)
    return None


class ImageSource:
    def __init__(self, file_path):
        self.file_name = file_path[file_path.rfind("/") + 1:]
        self.file_path = file_path

        img = Image.open(file_path)
        self.file = trim(img)
        img.close()

        self.width = self.file.width
        self.height = self.file.height

    def close(self):
        self.file.close()


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

    def save(self, file_name):
        new_image = Image.new("RGBA", (self.max_size, self.max_size))

        for image in self.images.values():
            new_image.paste(image["source"].file,
                            box=(image["left"], image["top"]))
            image["source"].close()

        trimed_image = trim(new_image)
        trimed_image.save(file_name)
        new_image.close()
        trimed_image.close()


class AtlasMaker:
    def __init__(self, images, max_size=2048, padding=2):
        self.max_size = max_size
        self.padding = padding

        self.atlases = []
        self.images = [ImageSource(image) for image in images]
        self.unused_images = set()

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

    def save(self):
        for i, atlas in enumerate(self.atlases):
            file_name = f"sprites-{i}.png"

            try:
                atlas.save(file_name)
            except Exception:
                logging.exception(f"{file_name} failed")
