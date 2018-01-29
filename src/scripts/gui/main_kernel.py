import json
import time
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename

import numpy as np
from pkg_resources import resource_filename
from scipy.special import binom

from ..processes.bm_wrapper import BM_Wrapper
from .main_gui import MainGUI
from .reader_kernel import ReaderKernel
from .export_kernel import ExportKernel

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
        self.row_map = []
        self.result_table = []
        self.app = None

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
            self.row_map = np.ones(len(self.data))
            self.update_overview()
            self.default_settings()

    def default_settings(self, app=None):
        if not app:
            app=self.app
        if self.age:
            app.settings["min_age"].set(str(min(self.age)))
            app.settings["max_age"].set(str(max(self.age)))
        else:
            try:
                app.settings["min_age"].set("N/A")
                app.settings["max_age"].set("N/A")
            except:
                pass
        if self.sex:
            app.settings["sex"].set(" ".join([str(x) for x in list(set(self.sex))]))
        else:
            app.settings["sex"].set("N/A")

    def update_overview(self):
        if self.header:
            self.app.build_overview(self.data, self.header)

    def cmd_export(self):
        if self.result_table:
            file_name = asksaveasfilename(defaultextension=".xlsx")
            if file_name is None: # asksaveasfile return `None` if dialog closed with "cancel".
                return
            ExportKernel(self, self.result_table, file_name)
    
    def cmd_execute(self):
        if self.app.col_map:
            data = np.array(self.data)
            data = np.delete(data, [i for i, col in enumerate(self.app.col_map) if not col], axis=1)
            if hasattr(self.row_map, "shape"):
                data = np.delete(data, [i for i, row in enumerate(self.row_map) if not row], axis=0)
            pos_val = self.get_vals(self.app.settings["pos_val"])
            neg_val = self.get_vals(self.app.settings["neg_val"])
            max_clust = int(self.app.settings["max_clust"].get())
            startTime = time.time()
            result_dictionary = BM_Wrapper().analyse(max_cluster=max_clust,
                                                     data=data,
                                                     pos_map=pos_val,
                                                     neg_map=neg_val)
            elapsedTime = time.time() - startTime
            print(elapsedTime)
            self.settings["exe_time"].append([int(self.app.info_text[1].get()), elapsedTime])
            self.save_settings()
            self.update_info()
            self.result_table = self.get_res_table(result_dictionary)
            self.app.build_result(self.result_table)

    def get_res_table(self, result_dictionary):
        sco_vec = result_dictionary["score_vec"]
        pat_vec = result_dictionary["pattern_vec"]
        pos_vec = result_dictionary["pos_vec"]
        neg_vec = result_dictionary["neg_vec"]

        header = [h for h, c in zip(self.header, self.app.col_map) if c]

        # First row with headers
        cols = len(header)
        styles = []
        for pattern in pat_vec:
            col_pattern = self._bin_array(int(pattern), cols)
            row_s = []
            for i, col in enumerate(col_pattern):
                if col:
                    row_s.append(header[i])
            styles.append(row_s)

        result_table = [[""]*(len(header)+1) for x in range(len(header)+4)]
        for i, row in enumerate(result_table):
            if i == 0:
                for j, _ in enumerate(row):
                    if not j == 0:
                        result_table[i][j] = j
            elif i == len(header)+1:
                for j, _ in enumerate(row):
                    if j == 0:
                        result_table[i][j] = "+"
                    else:
                        try:
                            result_table[i][j] = int(pos_vec[j-1])
                        except OverflowError:
                            result_table[0][j] = ""
            elif i == len(header)+2:
                for j, _ in enumerate(row):
                    if j == 0:
                        result_table[i][j] = "-"
                    else:
                        try:
                            result_table[i][j] = int(neg_vec[j-1])
                        except OverflowError:
                            pass
            elif i == len(header)+3:
                for j, _ in enumerate(row):
                    if j == 0:
                        result_table[i][j] = "Total"
                    else:
                        try:
                            result_table[i][j] = int(sco_vec[j-1])
                        except OverflowError:
                            pass
            else:
                for j, style in enumerate(styles):
                    if len(style) > i-1:
                        result_table[i][j+1] = style[i-1]
        return result_table

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
                if int(val) > sum(self.app.col_map):
                    self.app.settings["max_clust"].set(str(sum(self.app.col_map)))
            except ValueError:
                self.app.settings["max_clust"].set(str(sum(self.app.col_map)))
            self.update_info()

    def get_age_filter(self):
        age_bitmap = np.ones(len(self.data))
        if self.age:
            try:
                min_age = int(self.app.settings["min_age"].get())
                max_age = int(self.app.settings["max_age"].get())
                age_bitmap = np.logical_and(np.array(self.age) >= min_age,
                                            np.array(self.age) <= max_age)
            except ValueError:
                pass
        return age_bitmap

    def get_sex_filter(self):
        if self.sex:
            try:
                sex_bitmap = np.zeros(len(self.data))
                sexes = self.get_vals(self.app.settings["sex"])
                for sex in sexes:
                    sex_bitmap = np.logical_or(sex_bitmap,
                                               np.array(self.sex) == sex)
                return sex_bitmap
            except ValueError:
                pass
        return np.ones(len(self.data))

    def cmd_age_updated(self, *args):
        age_bitmap = self.get_age_filter()
        sex_bitmap = self.get_sex_filter()
        self.row_map = np.logical_and(age_bitmap, sex_bitmap)
        if self.app:
            self.update_info()

    def cmd_quit(self):
        self.root.destroy()

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
            # Update number of participants
            self.app.info_text[2].set("{:d}".format(int(np.sum(self.row_map))))
            # Update estimated time using linear interpolation
            dat = np.array(self.settings["exe_time"])
            #def lin_extrapolate(self, x, y, point):
            exe_times = self.lin_extrapolate(dat[:,0], dat[:,1], combs)[0]
            str_time = self.to_str_time(exe_times)
            self.app.info_text[3].set(str_time)

    def to_str_time(self, seconds):
        intervals = (
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )
        result = []

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(int(value), name))
                break
        if not result:
            return "{:0.2f}s".format(seconds)
        return ', '.join(result[:])

    def lin_extrapolate(self, x, y, point):
        x = np.array([x])
        x = np.concatenate((x, np.ones(np.shape(x))), axis=0).T
        y = np.array([y]).T
        m, c = np.linalg.lstsq(x, y)[0]
        return m*point + c

    def _bin_array(self, num, m):
        """Convert a positive integer num into an m-bit bit vector
        """
        return np.array(list(np.binary_repr(num).zfill(m))).astype(np.int8)