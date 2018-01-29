import tkinter as tk
from tkinter.colorchooser import *
from ..support.widgets import ColorWidget
from pkg_resources import resource_filename
import json

class ExportGUI(tk.Frame):
    def __init__(self, master, kernel):
        self.kernel = kernel
        self.master = master
        self.top_frame = tk.Frame(master, width=400, height=200)
        self.top_frame.pack(fill=tk.BOTH)
        self.master.resizable(width=False, height=False)

        self.settings = json.load(open(resource_filename("src.resources.settings",
                                                         "settings.json")))
        self.colors = self.build_color_chooser(self.settings)

        btn_frame = tk.Frame(master)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Export", command=self.kernel.cmd_export).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Cancel", command=self.kernel.cmd_cancel).pack(side=tk.LEFT)

    def build_color_chooser(self, settings):
        colors = {"color_1": tk.StringVar(self.master),
                  "color_2": tk.StringVar(self.master),
                  "color_3": tk.StringVar(self.master),
                  "font_color_1": tk.StringVar(self.master),
                  "font_color_2": tk.StringVar(self.master)}
        colors["color_1"].set(settings["color_1"])
        colors["color_2"].set(settings["color_2"])
        colors["color_3"].set(settings["color_3"])
        colors["font_color_1"].set(settings["font_color_1"])
        colors["font_color_2"].set(settings["font_color_2"])

        ColorWidget(self.top_frame, text="Color #1", color=colors["color_1"]).pack(fill=tk.X)
        ColorWidget(self.top_frame, text="Color #2", color=colors["color_2"]).pack(fill=tk.X)
        ColorWidget(self.top_frame, text="Color #3", color=colors["color_3"]).pack(fill=tk.X)
        ColorWidget(self.top_frame, text="Font color #1", color=colors["font_color_1"]).pack(fill=tk.X)
        ColorWidget(self.top_frame, text="Font color #2", color=colors["font_color_2"]).pack(fill=tk.X)
        return colors
