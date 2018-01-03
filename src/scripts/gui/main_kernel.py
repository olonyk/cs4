import json
import time
from tkinter import *
from tkinter.filedialog import askopenfilename

import numpy as np
from pkg_resources import resource_filename
from scipy.special import binom

from ..processes.bm_wrapper import BM_Wrapper
from .main_gui import MainGUI
from .reader_kernel import ReaderKernel
from scipy.linalg import pascal

class MainKernel(object):
    def __init__(self, args):
        # Read settings file
        self.settings = json.load(open(resource_filename("src.resources.settings",
                                                         "settings.json")))
        # Initialize variables
        self.data = []
        self.header = []
        self.age = []
        self.sex = []

        # Create the GUI
        self.root = Tk()
        self.root.title("CS4")
        self.root.minsize(width = 600, height = 600)
        self.app = MainGUI(self.root, self)

    def run(self):
        self.root.mainloop()
        self.root.destroy()

    def cmd_import(self):
        file_name = askopenfilename()
        if file_name:
            ReaderKernel(self, file_name)
            self.update_overview()

    def update_overview(self):
        if self.header:
            self.app.build_overview(self.data, self.header)

    def cmd_export(self):
        print("hi there, everyone!")
    
    def cmd_execute(self):
        if self.app.col_map:
            data = np.array(self.data)
            data = np.delete(data, [i for i, col in enumerate(self.app.col_map) if not col], axis=1)
            pos_val = self.get_vals(self.app.settings["pos_val"])
            neg_val = self.get_vals(self.app.settings["neg_val"])
            max_clust = int(self.app.settings["max_clust"].get())
            startTime = time.time()
            score_vec, pattern_vec = BM_Wrapper().analyse(caller=self,
                                                          data=data,
                                                          pos_map=pos_val,
                                                          neg_map=neg_val)
            elapsedTime = time.time() - startTime
            print(score_vec)
            print(pattern_vec)
            print(elapsedTime)
            self.settings["exe_time"].append([len(self.header), elapsedTime])
            self.update_info()
            self.save_settings()

    def get_vals(self, val_str_var):
        return [int(s) for s in val_str_var.get() if s.isdigit()]

    def save_settings(self):
        # Save the updated settings file.
        with open(resource_filename("src.resources.settings", "settings.json"), 'w') as jsonfile:
            json.dump(self.settings, jsonfile)

    def cmd_max_cluster_updated(self, *args):
        if self.app.settings["max_clust"].get():
            val = self.app.settings["max_clust"].get()
            try:
                if int(val) > len(self.app.col_map):
                    self.app.settings["max_clust"].set(str(len(self.app.col_map)))    
            except ValueError:
                self.app.settings["max_clust"].set(str(len(self.app.col_map)))
            self.update_info()
        #print("New value:", self.app.settings["max_clust"].get())

    def update_info(self):
        if self.app.col_map:
            nr_cols = sum(self.app.col_map)
            # Update number of columns
            self.app.info_text[0].set(str(nr_cols))
            # Update number of combination to check
            combs = 0
            for i in range(1, int(self.app.settings["max_clust"].get())+1):
                combs += binom(sum(self.app.col_map), i)
            self.app.info_text[1].set(str(int(combs)))
            # Update estimated time using linear interpolation
            dat = np.array(self.settings["exe_time"])
            exe_times = np.interp(nr_cols, dat[:,0], dat[:,1])
            self.app.info_text[2].set("{:0.2f}s".format(exe_times))
