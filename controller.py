import argparse
import os
import re

from packer import AtlasMaker
from packer.ui import start_ui


DEFAULT_RESULT_FOLDER = os.path.join(os.getcwd(), "result")
img_pattern = re.compile(r".+\.(?:(?:png)|(?:jpg)|(?:jpeg))")


def print_danger(text):
    """
    Print red text
    """

    print("\033[0;31m" + text + "\x1b[0m")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(title="Avalible Functionality",
                                        description="", help="",
                                        dest="subparser")
    atlas_parser = sub_parsers.add_parser("atlas")
    split_parser = sub_parsers.add_parser("split")

    # Atlas sub argument
    atlas_parser.add_argument("-u", "--ui", action="store_true",
                              help="Using UI mode", default=False)

    atlas_parser.add_argument("-i", "--images", action="append",
                              metavar="path", help="Images source path",
                              default=[])
    atlas_parser.add_argument("-f", "--folders", action="append",
                              metavar="parh", help="Scan folders path",
                              default=[])
    atlas_parser.add_argument("-t", "--trim", action="store_true",
                              default=False,
                              help="Trim the image when loading")
    atlas_parser.add_argument("-p", "--padding", type=int, default=3)

    atlas_parser.add_argument("--trim-result", action="store_true",
                              default=False,
                              help="Trim the result image")
    atlas_parser.add_argument("--result-folder", metavar="path",
                              default=DEFAULT_RESULT_FOLDER)
    atlas_parser.add_argument("--prefix", default="atlas-", metavar="string")

    # Split sub argument
    split_parser.add_argument("-i", "--image", metavar="path",
                              help="Image source path")
    split_parser.add_argument("--result-folder", metavar="path",
                              default=DEFAULT_RESULT_FOLDER)

    #normal
    #count row, col
    #size width, height

    args = parser.parse_args()

    if args.subparser is None:
        parser.print_help()
        exit()

    if args.subparser == "split":
        pass

    elif args.ui:
        os.chdir("packer")
        start_ui()

    else:
        if len(args.images) < 1 and len(args.folders) < 1:
            print_danger("Must assign images, use -i [image path]\n")
            parser.print_help()
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

        maker = AtlasMaker(padding=args.padding)
        maker.add_images(
            *images,
            trim=args.trim,
        )

        maker.make()
        maker.save(result_folder=args.result_folder, prefix=args.prefix,
                   trim=args.trim_result)

