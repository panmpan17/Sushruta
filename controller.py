import argparse
import os
import re

from packer import AtlasMaker
from packer.ui import start_ui


img_pattern = re.compile(r".+\.(?:(?:png)|(?:jpg)|(?:jpeg))")


def print_danger(text):
    """
    Print red text
    """

    print("\033[0;31m" + text + "\x1b[0m")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("method", default="console", nargs="?",
                        choices=("console", "ui"))
    parser.add_argument("-i", "--images", action="append", metavar="path",
                        help="Image source path", default=[])
    parser.add_argument("-f", "--folders", action="append", metavar="parh",
                        help="Scane folder path", default=[])
    parser.add_argument("-t", "--trim", action="store_true", default=False,
                        help="Trim the image when loading")
    parser.add_argument("--trim-result", action="store_true", default=False,
                        help="Trim the result image")
    parser.add_argument("--result-folder", default="result", metavar="path")
    parser.add_argument("--prefix", default="atlas-", metavar="string")

    args = parser.parse_args()

    if args.method == "console":
        if len(args.images) < 1 and len(args.folders) < 1:
            print_danger("Must assign images, use -i [image path]")
            exit()

        images = []

        for img in args.images:
            if not os.path.isfile(img):
                print_danger(f"Image '{img}' not exist")
                continue

            if bool(img_pattern.fullmatch(img)):
                images.append(img)

        for folder in args.folders:
            if not os.path.isdir(folder):
                print_danger(f"Folder '{folder}' not exist")

            for file in os.listdir(folder):
                if bool(img_pattern.fullmatch(file)):
                    images.append(os.path.join(folder, file))

        maker = AtlasMaker(padding=0)
        maker.add_images(
            *images,
            trim=args.trim,
        )

        maker.make()
        maker.save(folder=args.result_folder, prefix=args.prefix,
                   trim=args.trim_result)

    else:
        os.chdir("packer")
        start_ui()
