import argparse
import os
import re

from sushruta import AtlasMaker, ImageSpliter, ImageTile
from sushruta.ui import start_ui


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
    tile_parser = sub_parsers.add_parser("tile")
    sub_split_parsers = split_parser.add_subparsers(dest="splitsubargs")


    # Atlas sub argument
    atlas_parser.add_argument("-u", "--ui", action="store_true",
                              help="Using UI mode", default=False)

    atlas_parser.add_argument("-i", "--images", action="append",
                              metavar="path", help="Images source path",
                              default=[])
    atlas_parser.add_argument("-f", "--folders", action="append",
                              metavar="path", help="Scan folders path",
                              default=[])
    atlas_parser.add_argument("-t", "--trim", action="store_true",
                              default=False,
                              help="Trim the image when loading")
    atlas_parser.add_argument("-p", "--padding", type=int, default=3)

    atlas_parser.add_argument("--deep-scan", action="append", metavar="path",
                              help="Deep scan folders path", default=[])
    atlas_parser.add_argument("--trim-result", action="store_true",
                              default=False,
                              help="Trim the result image")
    atlas_parser.add_argument("--result-folder", metavar="path",
                              default=DEFAULT_RESULT_FOLDER)
    atlas_parser.add_argument("--prefix", default="atlas-", metavar="string")

    # Split sub argument
    split_parser.add_argument("image", help="Image source path")
    split_parser.add_argument("--result-folder", metavar="path",
                              default=DEFAULT_RESULT_FOLDER)
    split_count_parser = sub_split_parsers.add_parser("count")
    split_size_parser = sub_split_parsers.add_parser("size")

    split_count_parser.add_argument("row", type=int)
    split_count_parser.add_argument("col", type=int)

    split_size_parser.add_argument("width", type=int)
    split_size_parser.add_argument("height", type=int)

    # Tile sub argument
    tile_parser.add_argument("image", help="Image source path")
    tile_parser.add_argument("width", type=int)
    tile_parser.add_argument("height", type=int)
    tile_parser.add_argument("--result-folder", metavar="path",
                             default=DEFAULT_RESULT_FOLDER)

    args = parser.parse_args()

    if args.subparser is None:
        parser.print_help()
        exit()

    if args.subparser == "split":
        if args.splitsubargs is None:
            ImageSpliter.split(args.image, result_folder=args.result_folder)

        elif args.splitsubargs == "count":
            ImageSpliter.split_by_count(args.image, args.row, args.col,
                                        result_folder=args.result_folder)

        elif args.splitsubargs == "size":
            ImageSpliter.split_by_size(args.image, args.width, args.height,
                                       result_folder=args.result_folder)

    elif args.subparser == "tile":
        ImageTile.tile_by_size(args.image, args.width, args.height,
                               result_folder=args.result_folder)

    elif args.ui:
        os.chdir("sushruta")
        start_ui()

    else:
        if (len(args.images) < 1 and len(args.folders) < 1 and
                len(args.deep_scan) < 1):
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

        for folder in args.deep_scan:
            for root, _, file_names in os.walk(folder):
                for file_name in file_names:
                    if bool(img_pattern.fullmatch(file_name)):
                        images.append(os.path.join(root, file_name))

        maker = AtlasMaker(padding=args.padding)
        maker.add_images(
            *images,
            trim=args.trim,
        )

        maker.make()
        maker.save(result_folder=args.result_folder, prefix=args.prefix,
                   trim=args.trim_result)

