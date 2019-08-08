from packer import AtlasMaker

if __name__ == "__main__":
    maker = AtlasMaker(padding=0)
    maker.add_images(
        "/Users/michael/Desktop/1.png",
        "/Users/michael/Desktop/2.png",
        "/Users/michael/Desktop/3.png",
        "/Users/michael/Desktop/4.png",
        trim=False,
    )

    maker.make()
    maker.save(folder="result", prefix="atlas-", trim=False)
