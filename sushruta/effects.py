import random

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


img = Image.open("reference.jpg")
image = img.convert("RGBA")
img.close()

points = set()
alpha_map = [[255 for e in range(image.width)] for i in range(image.height)]

for x in range(image.width):
    for y in range(50):
        chance = random.randint(0, 50)
        if chance < (55 - y * 1.7):
            points.add((x, y))

    miny = image.height - 50
    for y in range(miny, image.height):
        chance = random.randint(0, 50)
        if chance < (55 - (50 - y + miny)):
            points.add((x, y))

for y in range(image.height):
    for x in range(50):
        chance = random.randint(0, 50)
        if chance < (55 - x * 1.7):
            points.add((x, y))

    minx = image.width - 50
    for x in range(minx, image.width):
        chance = random.randint(0, 50)
        if chance < (55 - (50 - x + minx)):
            points.add((x, y))

for pos in points:
    for x in range(pos[0] - 1, pos[0] + 2):
        for y in range(pos[1] - 1, pos[1] + 2):
            if (x >= 0 and y >= 0 and x < image.width and y < image.height):
                alpha_map[y][x] *= 0.5

for _ in range(3):
    for y, row in enumerate(alpha_map):
        for x, num in enumerate(row):
            nums = find_surround(alpha_map, x, y)
            alpha_map[y][x] = sum(nums) / len(nums)

# new_img = Image.new("RGB", image.size)
for y, row in enumerate(alpha_map):
    for x, num in enumerate(row):
        color = list(image.getpixel((x, y)))
        color[3] = int(num)
        image.putpixel((x, y), tuple(color))

# new_img.save("test-2.png")
# new_img.close()

image.save("test-2.png")
image.close()
