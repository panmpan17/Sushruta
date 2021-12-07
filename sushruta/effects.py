import random
import os

from PIL import Image  # , ImageDraw


def find_surround(_map, x, y):
    surrounds = []
    for i in range(x - 1, x + 2):
        for e in range(y - 1, y + 2):
            if x == i and y == e:
                continue

            if i >= 0 and e >= 0:
                try:
                    surrounds.append(_map[e][i])
                except IndexError:
                    pass

    return surrounds


class BorderBlurHandler:
    def __init__(self, file_path, destination_folder) -> None:
        self.file_path = file_path
        self.destination_folder = destination_folder

        original_image = Image.open(file_path)
        self.image = original_image.convert("RGBA")
        original_image.close()

        self.points = set()
        self.alpha_map = [[255 for e in range(self.image.width)] for i in range(self.image.height)]
    
    def start(self):
        for x in range(self.image.width):
            for y in range(50):
                chance = random.randint(0, 50)
                if chance < (55 - y * 1.7):
                    self.points.add((x, y))

            miny = self.image.height - 50
            for y in range(miny, self.image.height):
                chance = random.randint(0, 50)
                if chance < (55 - (50 - y + miny)):
                    self.points.add((x, y))

        for y in range(self.image.height):
            for x in range(50):
                chance = random.randint(0, 50)
                if chance < (55 - x * 1.7):
                    self.points.add((x, y))

            minx = self.image.width - 50
            for x in range(minx, self.image.width):
                chance = random.randint(0, 50)
                if chance < (55 - (50 - x + minx)):
                    self.points.add((x, y))

        for point in self.points:
            for x in range(point[0] - 1, point[0] + 2):
                for y in range(point[1] - 1, point[1] + 2):
                    if (x >= 0 and y >= 0 and x < self.image.width and y < self.image.height):
                        self.alpha_map[y][x] *= 0.5

        for _ in range(3):
            for y, row in enumerate(self.alpha_map):
                for x, num in enumerate(row):
                    nums = find_surround(self.alpha_map, x, y)
                    self.alpha_map[y][x] = sum(nums) / len(nums)

        for y, row in enumerate(self.alpha_map):
            for x, num in enumerate(row):
                color = list(self.image.getpixel((x, y)))
                color[3] = int(num)
                self.image.putpixel((x, y), tuple(color))

    def save(self, file_name):
        self.image.save(os.path.join(self.destination_folder, file_name))
        self.image.close()
