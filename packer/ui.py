import os
import re
import tkinter
import subprocess
from tkinter import filedialog, messagebox
from .atlas_maker import AtlasMaker, PSDSouce
import tkouter

img_pattern = re.compile(r".+\.(?:(?:png)|(?:jpg)|(?:jpeg))")


def clear():
    subprocess.call(["clear"])


def print_success(*args):
    """
    Print green text
    """

    print("\033[0;32m", *args, "\x1b[0m")


class MenuItem:
    def __init__(self, name, callback=None, args=(), kwargs={}):
        self.name = name
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        self.callback(*self.args, **self.kwargs)


class App:
    def __init__(self):
        self.menu = []
        self.images = []

    def setup_menu(self):
        self.menu.append(MenuItem("Status", self.show_status))
        self.menu.append(MenuItem("Add File", self.ask_file))
        self.menu.append(MenuItem("Scan Folder", self.scan_folder))
        self.menu.append(MenuItem("Scan Folder (Deep Scan)",
                                  self.scan_folder, kwargs={"deep": True}))
        self.menu.append(MenuItem("Export", self.export))
        self.menu.append(MenuItem("Quit", self.quit))

    def print_menu(self):
        for i, item in enumerate(self.menu):
            print(i, item.name)

    def run(self):
        r = tkinter.Tk()
        r.withdraw()

        while True:
            try:
                self.print_menu()
                cmd_index = int(input("Input: "))
                clear()
            except ValueError:
                clear()
                print("Error.")
                continue
            except KeyboardInterrupt:
                self.quit()

            if cmd_index >= len(self.menu):
                print("Error.")
                continue

            item = self.menu[cmd_index]
            if item.callback is not None:
                item.execute()

    def quit(self):
        exit()

    def show_status(self):
        print("\nImages:\n")

        for i, image in enumerate(self.images):
            print(i, image)
        print(f"Total Image: {len(self.images)}\n")

    def ask_file(self):
        filenames = filedialog.askopenfilenames(
            initialdir=os.getcwd(),
            title="Select Image",
            filetypes=(("Png", "*.png"), ("Jpg", "*.jpg"), ("Jpeg", "*.jpeg")))

        for filename in filenames:
            print(filename)
            self.images.append(filename)

    def scan_folder(self, deep=False):
        folder = filedialog.askdirectory(
            title="Select Directory to Scan Images")

        total_added = 0
        if deep:
            pass
        else:
            for filename in os.listdir(folder):
                if bool(img_pattern.fullmatch(filename)):
                    total_added += 1
                    self.images.append(os.path.join(folder, filename))
        print_success(total_added, "Images Added")

    def export(self):
        try:
            max_size = int(input("Max size (2048): "))
        except ValueError:
            max_size = 2048
        try:
            padding = int(input("Padding (2): "))
        except ValueError:
            padding = 2

        maker = AtlasMaker(self.images, max_size, padding)
        maker.make()
        maker.save()


class ButtonsView(tkouter.TkOutWidget):
    layout = "html/buttons.html"

    max_size = tkouter.StringField(default='2048')
    padding = tkouter.StringField(default='2')
    trimming = tkouter.BoolField(default=True)

    def __init__(self, *args, **kwargs):
        self.list_view = None
        self.images = set()

        super().__init__(*args, **kwargs)

    def assign_list_view(self, list_view):
        self.list_view = list_view

    def add_images(self, *args):
        filenames = filedialog.askopenfilenames(
            initialdir=os.getcwd(),
            title="Select Image",
            filetypes=(("Png", "*.png"), ("Jpg", "*.jpg"), ("Jpeg", "*.jpeg")))

        total_added = 0
        for filename in filenames:
            if filename not in self.images:
                total_added += 1
                self.images.add(filename)
                self.list_view.insert("end", filename)

        if len(self.images) > 0:
            self.export_btn.config(state="normal")

        messagebox.showinfo("Totoal Added Images", str(total_added))

    def scan_directory(self, *args):
        folder = filedialog.askdirectory(
            title="Select Directory to Scan Images")

        total_added = 0
        for filename in os.listdir(folder):
            if bool(img_pattern.fullmatch(filename)):
                path = os.path.join(folder, filename)

                if path not in self.images:
                    total_added += 1
                    self.images.add(path)
                    self.list_view.insert("end", path)

        messagebox.showinfo("Totoal Added Images", str(total_added))

        if len(self.images) > 0:
            self.export_btn.config(state="normal")

    def scan_directory_deep(self, *args):
        folder = filedialog.askdirectory(
            title="Select Directory to Scan Images")

        total_added = 0
        for root, _, filenames in os.walk(folder):
            for filename in filenames:
                if bool(img_pattern.fullmatch(filename)):
                    path = os.path.join(root, filename)

                    if path not in self.images:
                        total_added += 1
                        self.images.add(path)
                        self.list_view.insert("end", path)

        messagebox.showinfo("Totoal Added Images", str(total_added))

        if len(self.images) > 0:
            self.export_btn.config(state="normal")

    def export_psd(self, *args):
        filenames = filedialog.askopenfilenames(
            initialdir=os.getcwd(),
            title="Select PSD file",
            filetypes=(("PSD", "*.psd"), ))

        try:
            max_size = int(self.max_size)
        except ValueError:
            max_size = 2048
        try:
            padding = int(self.padding)
        except ValueError:
            padding = 2

        maker = AtlasMaker(max_size, padding)
        for filename in filenames:
            psd = PSDSouce(filename, trimming=self.trimming)
            psd.load()
            maker.add_images(*psd.images)

        maker.make()
        maker.save()

    def add_psd(self, *args):
        # filenames = filedialog.askopenfilenames(
        #     initialdir=os.getcwd(),
        #     title="Select PSD file",
        #     filetypes=(("PSD", "*.psd"), ))

        # for filename in filenames:
        #     psd = PSDSouce(filename)
        #     psd.load()
        #     maker.add_images(*psd.images)
        pass

    def delete_selected(self, *args):
        selection = list(self.list_view.curselection())
        selection.reverse()

        for index in selection:
            self.images.remove(self.list_view.get(index))
            self.list_view.delete(index, index)

        if len(self.images) == 0:
            self.export_btn.config(state="disabled")

    def clear_images(self, *args):
        result = messagebox.askquestion(
            "Clear All Images?",
            "Are you sure you want to exit the application\nCan't be undo",
            icon="warning")

        if result == "yes":
            self.list_view.delete(0, tkinter.END)
            self.images.clear()
            self.export_btn.config(state="disabled")

    def export(self, *args):
        try:
            max_size = int(self.max_size)
        except ValueError:
            max_size = 2048
        try:
            padding = int(self.padding)
        except ValueError:
            padding = 2

        maker = AtlasMaker(max_size, padding)
        maker.add_images(*self.images)
        maker.make()
        maker.save()

    def quit(self, *args):
        exit()


class ListView(tkouter.TkOutWidget):
    layout = "html/list.html"

    def get(self, *args):
        return self.listbox.get(*args)

    def insert(self, *args):
        self.listbox.insert(*args)

    def delete(self, *args):
        self.listbox.delete(*args)

    def curselection(self):
        return self.listbox.curselection()


def start_ui():
    root = tkinter.Tk()
    root.resizable(False, False)
    root.configure(background="#1B2126")

    buttons_view = ButtonsView(root)
    list_view = ListView(root)

    buttons_view.assign_list_view(list_view)

    buttons_view.pack(side=tkinter.LEFT)
    list_view.pack(side=tkinter.LEFT)

    root.bind_all("<BackSpace>", buttons_view.delete_selected)
    root.bind_all("<Command-BackSpace>", buttons_view.clear_images)

    root.bind_all("<Command-e>", buttons_view.export)

    root.mainloop()
