import json
import os

from PIL import Image, ImageDraw


SIDE = ((-1, 0), (1, 0), (0, -1), (0, 1))
AROUND = ((-1, -1), (0, -1), (1, -1),
          (-1, 0), (0, 0), (1, 0),
          (-1, 1), (0, 1), (1, 1))


class ImageSpliter:
    @classmethod
    def get_img_name(cls, file_path):
        return ".".join(file_path.split("/")[-1].split(".")[:-1])

    @classmethod
    def scan_region(cls, img, pos):
        pixels = set()
        coords_unchecked = set([pos])

        while len(coords_unchecked) > 0:
            pos = coords_unchecked.pop()
            pixels.add(pos)

            for vec in AROUND:
                new_pos = pos[0] + vec[0], pos[1] + vec[1]

                if (img.width > new_pos[0] >= 0 and
                        img.height > new_pos[1] >= 0):
                    if new_pos in pixels:
                        continue

                    color = img.getpixel(new_pos)
                    if color[3] <= 20:
                        continue

                    coords_unchecked.add(new_pos)

        return pixels

    @classmethod
    def scan_regions(cls, img):
        regions = []
        scaned = set()

        for x in range(img.width):
            for y in range(img.height):
                pos = (x, y)
                color = img.getpixel(pos)

                # If alpha level is 0, aka invisible
                if color[3] <= 20:
                    continue

                if pos in scaned:
                    continue

                regions.append(cls.scan_region(img, pos))

                for pos in regions[-1]:
                    scaned.add(pos)

        return regions

    @classmethod
    def get_region_bound(cls, region):
        min_x = max_x = min_y = max_y = None

        for pos in region:
            if min_x is None:
                min_x = pos[0]
                max_x = pos[0]
                min_y = pos[1]
                max_y = pos[1]
                continue

            if pos[0] < min_x:
                min_x = pos[0]
            if pos[0] > max_x:
                max_x = pos[0]

            if pos[1] < min_y:
                min_y = pos[1]
            if pos[1] > max_y:
                max_y = pos[1]

        return (min_x, min_y, max_x, max_y)

    @classmethod
    def debug_draw(cls, _img, name="test.png", bounds=None, regions=None):
        img = _img.copy()

        draw = ImageDraw.Draw(img)

        if regions is not None:
            for region in regions:
                draw.point(list(region), fill=(255, 0, 0, 25))

        if bounds is not None:
            for bound in bounds:
                draw.rectangle(bound,  # fill=(255, 0, 0, 25),
                               outline=(255, 0, 0, 255))

        del draw

        img.save(name)
        img.close()

    @classmethod
    def crop_bound(cls, img, bound):
        return (bound[0], bound[1]), img.crop(bound)

    @classmethod
    def save_crops(cls, crops, file_name, result_folder):
        data = {}
        for i, (pos, crop) in enumerate(crops):
            path = os.path.join(result_folder, file_name + f"_{i}.png")
            try:
                crop.save(path)
            except SystemError:
                os.remove(path)
            data[path] = list(pos)

            crop.close()

        json.dump(data, open(
                  os.path.join(result_folder, file_name + ".json"), "w"))

    @classmethod
    def split(cls, file_path, result_folder=""):
        try:
            img = Image.open(file_path)
        except FileNotFoundError:
            return "File not exist"

        # regions = cls.scan_regions(img)
        # bounds = [cls.get_region_bound(region) for region in regions]
        # cls.debug_draw(img, bounds=bounds, regions=regions)
        cls.save_crops([cls.crop_bound(img, cls.get_region_bound(region))
                        for region in cls.scan_regions(img)],
                       cls.get_img_name(file_path), result_folder)

        img.close()

    @classmethod
    def split_by_count(cls, file_path, row_num, col_num, result_folder=""):
        try:
            img = Image.open(file_path)
        except FileNotFoundError:
            return "File not exist"

        row_size = int(img.width / row_num)
        col_size = int(img.height / col_num)

        if file_path.endswith(".gif"):
            file_path = file_path.replace(".gif", "")

            for row in range(row_num):
                for col in range(col_num):
                    left, top = row * row_size, col * col_size
                    right, bottom = left + row_size, top + col_size

                    gifs = []
                    for i in range(img.n_frames):
                        img.seek(i)
                        new_img = img.crop((left, top, right, bottom))
                        gifs.append(new_img)

                    gifs[0].save(
                        os.path.join(result_folder,
                                        f"{file_path}-{row}-{col}.gif"),
                        format="GIF", append_images=gifs[1:], save_all=True,
                        duration=100, loop=0, transparency=0,
                        background=100, disposal=3)

        else:
            for row in range(row_num):
                for col in range(col_num):
                    left, top = row * row_size, col * col_size
                    right, bottom = left + row_size, top + col_size
                    new_img = img.crop((left, top, right, bottom))
                    new_img.save(os.path.join(result_folder,
                                              f"{file_path}-{row}-{col}.png"),
                                 "PNG")
                    new_img.close()

            img.close()

    @classmethod
    def split_by_size(cls, file_path, width, height, result_folder=""):
        try:
            img = Image.open(file_path)
        except FileNotFoundError:
            return "File not exist"

        if img.height > height:
            return

        file_name = cls.get_img_name(file_path)

        offsetX = 0
        i = 0
        while True:
            new_width = offsetX + width
            if new_width >= img.width:
                new_img = img.crop((offsetX, 0, img.width, img.height))
                new_img.save(os.path.join(result_folder,
                                          f"{file_name}-{i}.png"),
                             "PNG")
                new_img.close()
                break

            new_img = img.crop((offsetX, 0, new_width, img.height))
            new_img.save(os.path.join(result_folder,
                                      f"{file_name}-{i}.png"),
                         "PNG")

            new_img.close()
            offsetX += width
            i += 1

    @classmethod
    def crop(cls, file_path, x, y, width, height, result_folder=""):
        try:
            img = Image.open(file_path)
        except FileNotFoundError:
            return "File not exist"

        file_name = cls.get_img_name(file_path)

        if file_path.endswith(".gif"):
            file_path = file_path.replace(".gif", "")

            gifs = []
            for i in range(img.n_frames):
                img.seek(i)
                new_img = img.crop((x, y, x + width, y + height))
                gifs.append(new_img)

            gifs[0].save(
                os.path.join(result_folder,
                             f"{file_name}-{x},{y},{width},{height}.gif"),
                format="GIF", append_images=gifs[1:], save_all=True,
                duration=100, loop=0, transparency=0, background=255,
                disposal=3)

        else:
            new_img = img.crop((x, y, x + width, y + height))
            new_img.save(
                os.path.join(result_folder,
                             f"{file_name}-{x},{y},{width},{height}.png"),
                "PNG")
            new_img.close()
        img.close()


if __name__ == "__main__":
    # ImageSpliter.split("508-2.png")
    ImageSpliter.split_by_size("front.png", 1920, 1080)
