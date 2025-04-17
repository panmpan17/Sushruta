import argparse
import os
import re

from sushruta import AtlasMaker, ImageSpliter, ImageTile, Manipulator,\
                     BorderBlurHandler


DEFAULT_RESULT_FOLDER = os.path.join(os.getcwd(), "result")
img_pattern = re.compile(r".+\.(?:(?:png)|(?:jpg)|(?:jpeg))")


class Controller:
    @staticmethod
    def print_danger(text):
        """
        Print red text
        """

        print("\033[0;31m" + text + "\x1b[0m")

    def __init__(self):
        self.parser = None
        self.args = None

    def setup_parser(self):
        self.parser = argparse.ArgumentParser()
        sub_parsers = self.parser.add_subparsers(
            title="Avalible Functionality", description="", help="",
            dest="subparser")
        atlas_parser = sub_parsers.add_parser("atlas")
        split_parser = sub_parsers.add_parser("split")
        tile_parser = sub_parsers.add_parser("tile")
        crop_parser = sub_parsers.add_parser("crop")
        psd_parser = sub_parsers.add_parser("psd-split")
        blur_border_parser = sub_parsers.add_parser("blur-border")
        tune_multiplier_parser = sub_parsers.add_parser("tune-multiplier")
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

        atlas_parser.add_argument("--deep-scan", action="append",
                                  metavar="path",
                                  help="Deep scan folders path", default=[])
        atlas_parser.add_argument("--trim-result", action="store_true",
                                  default=False,
                                  help="Trim the result image")
        atlas_parser.add_argument("--result-folder", metavar="path",
                                  default=DEFAULT_RESULT_FOLDER)
        atlas_parser.add_argument("--prefix", default="atlas-",
                                  metavar="string")

        # Split sub argument
        split_parser.add_argument("image", help="Image source path")
        split_parser.add_argument("--result-folder", metavar="path",
                                  default=DEFAULT_RESULT_FOLDER)
        split_count_parser = sub_split_parsers.add_parser("count")
        split_size_parser = sub_split_parsers.add_parser("size")
        sub_split_parsers.add_parser("region")

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

        # Crop sub argument
        crop_parser.add_argument("image", help="Image source path")
        crop_parser.add_argument("x", type=int)
        crop_parser.add_argument("y", type=int)
        crop_parser.add_argument("width", type=int)
        crop_parser.add_argument("height", type=int)
        crop_parser.add_argument("--result-folder", metavar="path",
                                 default=DEFAULT_RESULT_FOLDER)

        # Manipule argument
        tune_multiplier_parser.add_argument("image", help="Image source path")
        tune_multiplier_parser.add_argument("-r", "--red", type=float,
                                            default=1.0)
        tune_multiplier_parser.add_argument("-g", "--green", type=float,
                                            default=1.0)
        tune_multiplier_parser.add_argument("-b", "--blue", type=float,
                                            default=1.0)
        tune_multiplier_parser.add_argument("-a", "--alpha", type=float,
                                            default=1.0)
        tune_multiplier_parser.add_argument("--result-folder", metavar="path",
                                            default=DEFAULT_RESULT_FOLDER)

        # PSD split argument
        psd_parser.add_argument("psd", help="Photoshop file source path")
        psd_parser.add_argument("--result-folder", metavar="path",
                                default=DEFAULT_RESULT_FOLDER)

        # Blur border arguemtn
        blur_border_parser.add_argument("image", help="Image source path")
        blur_border_parser.add_argument("result", help="Result image name")
        blur_border_parser.add_argument("--result-folder", metavar="path",
                                        default=DEFAULT_RESULT_FOLDER)

        self.args = self.parser.parse_args()

    def analyze_args(self):
        if self.args.subparser is None:
            self.parser.print_help()
            exit()

        if self.args.subparser == "split":
            self.handle_split_subparser()

        elif self.args.subparser == "tile":
            ImageTile.tile_by_size(self.args.image, self.args.width,
                                   self.args.height,
                                   result_folder=self.args.result_folder)

        elif self.args.subparser == "crop":
            ImageSpliter.crop(self.args.image, self.args.x, self.args.y,
                              self.args.width, self.args.width,
                              result_folder=self.args.result_folder)

        elif self.args.subparser == "tune-multiplier":
            self.handle_tune_multiplier()

        elif self.args.subparser == "psd-split":
            from sushruta.psd_split import PSDSplitter
            splitter = PSDSplitter(self.args.psd, self.args.result_folder)
            splitter.start()

        elif self.args.subparser == "blur-border":
            handler = BorderBlurHandler(self.args.image, self.args.result_folder)
            handler.start()
            handler.save(self.args.result)

        elif self.args.ui:
            from sushruta.ui import start_ui
            os.chdir("sushruta")
            start_ui()

        else:
            self.handle_atlas_maker()

    def handle_split_subparser(self):
        if self.args.splitsubargs == "region":
            ImageSpliter.split(self.args.image,
                               result_folder=self.args.result_folder)

        elif self.args.splitsubargs == "count":
            ImageSpliter.split_by_count(self.args.image, self.args.row,
                                        self.args.col,
                                        result_folder=self.args.result_folder)

        elif self.args.splitsubargs == "size":
            ImageSpliter.split_by_size(self.args.image, self.args.width,
                                       self.args.height,
                                       result_folder=self.args.result_folder)

        else:
            self.parser.print_help()

    def handle_tune_multiplier(self):
        Manipulator.tune_multiplier(self.args.image,
                                    (self.args.red, self.args.green,
                                     self.args.blue, self.args.alpha),
                                    result_folder=self.args.result_folder)

    def handle_atlas_maker(self):
        if (len(self.args.images) < 1 and len(self.args.folders) < 1 and
                len(self.args.deep_scan) < 1):
            Controller.print_danger(
                "Must assign images, use -i [image path]\n")
            self.parser.print_help()
            exit()

        images = []

        for img in self.args.images:
            if not os.path.isfile(img):
                Controller.print_danger(f"Image '{img}' not exist")
                continue

            if bool(img_pattern.fullmatch(img)):
                images.append(img)

        for folder in self.args.folders:
            if not os.path.isdir(folder):
                Controller.print_danger(f"Folder '{folder}' not exist")

            for file in os.listdir(folder):
                if bool(img_pattern.fullmatch(file)):
                    images.append(os.path.join(folder, file))

        for folder in self.args.deep_scan:
            for root, _, file_names in os.walk(folder):
                for file_name in file_names:
                    if bool(img_pattern.fullmatch(file_name)):
                        images.append(os.path.join(root, file_name))

        maker = AtlasMaker(padding=self.args.padding)
        maker.add_images(
            *images,
            trim=self.args.trim,
        )

        maker.make()
        maker.save(result_folder=self.args.result_folder,
                   prefix=self.args.prefix,
                   trim=self.args.trim_result)


if __name__ == "__main__":
    controller = Controller()
    controller.setup_parser()
    controller.analyze_args()
