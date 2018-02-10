import json
import sys
from os.path import dirname, isfile, join
from tkinter import (BOTH, GROOVE, LEFT, Button, Checkbutton, E, Entry, Frame,
                     Grid, IntVar, Label, Menu, N, OptionMenu, S, StringVar, W,
                     X)

from pkg_resources import resource_filename

from ..support.widgets import ColorWidget


class ExportGUI(Frame):
    def __init__(self, master, kernel):
        self.kernel = kernel
        self.master = master
        master.title("Export")
        self.top_frame = Frame(master, width=400, height=200)
        self.top_frame.pack(fill=BOTH)
        self.master.resizable(width=False, height=False)

        if getattr(sys, 'frozen', False):
                # We are running in a bundle, figure out the bundle dir.
                bundle_dir = sys._MEIPASS
                # Find the settings file.
                self.sfile = join(bundle_dir, "src","resources", "settings", "settings.json")
        else:
                # We are running in a normal Python environment.
                # Find the settings file.
                self.sfile = join(dirname(dirname(dirname(__file__))), "resources", "settings", "settings.json")
        # Read settings file
        self.settings = json.load(open(self.sfile))

        self.colors = self.build_color_chooser(self.settings)

        btn_frame = Frame(master)
        btn_frame.pack(fill=X)
        Button(btn_frame, text="Export", command=self.kernel.cmd_export).pack(side=LEFT)
        Button(btn_frame, text="Cancel", command=self.kernel.cmd_cancel).pack(side=LEFT)

    def build_color_chooser(self, settings):
        colors = {"color_1": StringVar(self.master),
                  "color_2": StringVar(self.master),
                  "color_3": StringVar(self.master),
                  "font_color_1": StringVar(self.master),
                  "font_color_2": StringVar(self.master)}
        colors["color_1"].set(settings["color_1"])
        colors["color_2"].set(settings["color_2"])
        colors["color_3"].set(settings["color_3"])
        colors["font_color_1"].set(settings["font_color_1"])
        colors["font_color_2"].set(settings["font_color_2"])

        ColorWidget(self.top_frame, text="Color #1", color=colors["color_1"]).pack(fill=X)
        ColorWidget(self.top_frame, text="Color #2", color=colors["color_2"]).pack(fill=X)
        ColorWidget(self.top_frame, text="Color #3", color=colors["color_3"]).pack(fill=X)
        ColorWidget(self.top_frame, text="Font color #1", color=colors["font_color_1"]).pack(fill=X)
        ColorWidget(self.top_frame, text="Font color #2", color=colors["font_color_2"]).pack(fill=X)
        return colors
