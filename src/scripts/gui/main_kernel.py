import json
import sys
import time
from os.path import dirname, isfile, join
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

from numpy import (array, asarray, binary_repr, concatenate, delete, int8,
                   linalg, logical_and, logical_or, ones, shape, zeros)
from scipy.special import binom

from ..processes.bm_wrapper import BM_Wrapper
from .export_kernel import ExportKernel
from .main_gui import MainGUI
from .preview_kernel import PreviewKernel
from .reader_kernel import ReaderKernel
from ..support.widgets import ViewLog

class MainKernel(object):
    def __init__(self, args):
        if getattr(sys, 'frozen', False):
            # We are running in a bundle, figure out the bundle dir.
            bundle_dir = sys._MEIPASS
            # Redirect stdout and stderr to log behaivour.
            stdout_file = join(bundle_dir, "src", "resources", "settings", "stdout.txt")
            sys.stdout = open(stdout_file, 'w')
            sys.stderr = open(stdout_file, 'w')
            # Find the settings file.
            self.sfile = join(bundle_dir, "src", "resources", "settings", "settings.json")
        else:
            # We are running in a normal Python environment.
            # Find the settings file.
            self.sfile = join(dirname(dirname(dirname(__file__))),
                              "resources",
                              "settings",
                              "settings.json")
        # Read settings file
        self.settings = json.load(open(self.sfile))

        # Initialize variables
        self.data = []
        self.header = []
        self.age = []
        self.sex = []
        self.ffan = {}
        self.row_map = []
        self.result_table = []
        self.app = None

        # Create the GUI
        self.root = Tk()
        self.root.title("CS4")
        self.root.minsize(width = 600, height = 600)
        self.app = MainGUI(self.root, self)

    def run(self):
        print("Main Kernel running")
        while True:
            try:
                self.root.mainloop()
                break
            except UnicodeDecodeError:
                pass
        self.root.destroy()

    def cmd_import(self, *args):
        print("CMD import")
        file_name = askopenfilename()
        if file_name:
            ReaderKernel(self, file_name)
            self.row_map = ones(len(self.data))
            self.update_overview()
            self.default_settings()

    def cmd_view_log(self, *args):
        print("CMD view log")
        args = ()
        ViewLog()
        

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
        if self.ffan:
            app.settings["ffan_list"] = self.ffan.keys()
            app.update_ffan()

    def update_overview(self):
        if self.header:
            self.app.build_overview(self.data, self.header)

    def cmd_export(self):
        print("CMD export")
        if self.result_table:
            file_name = asksaveasfilename(defaultextension=".xlsx")
            if file_name is None: # asksaveasfile return `None` if dialog closed with "cancel".
                return
            ExportKernel(self, self.result_table, file_name)
    
    def cmd_execute(self):
        print("CMD execute")
        if self.app.col_map:
            data = array(self.data)
            data = delete(data, [i for i, col in enumerate(self.app.col_map) if not col], axis=1)
            if hasattr(self.row_map, "shape"):
                data = delete(data, [i for i, row in enumerate(self.row_map) if not row], axis=0)
            print("shape(data):", shape(data))
            # Bad settings
            if int(self.app.settings["max_clust"].get()) == 0 or not shape(data)[1]:
                return
            
            meta_data = {"pos_val":self.get_vals(self.app.settings["pos_val"]),
                         "neg_val":self.get_vals(self.app.settings["neg_val"]),
                         "max_clust":int(self.app.settings["max_clust"].get()),
                         "min_clust":int(self.app.settings["min_clust"].get()),
                         "min_age":self.app.settings["min_age"].get(),
                         "max_age":self.app.settings["max_age"].get(),
                         "sex":self.app.settings["sex"].get(),
                         "ffan":self.app.settings["ffan_var"].get()}
            pos_val = self.get_vals(self.app.settings["pos_val"])
            neg_val = self.get_vals(self.app.settings["neg_val"])
            print(meta_data)
            max_clust = int(self.app.settings["max_clust"].get())
            startTime = time.time()
            result_dictionary = BM_Wrapper().analyse(max_cluster=max_clust,
                                                     data=data,
                                                     pos_map=pos_val,
                                                     neg_map=neg_val)
            elapsedTime = time.time() - startTime
            print("Elapsed time:", elapsedTime)
            meta_data["elapsedTime"] = self.to_str_time(elapsedTime, times=2)
            self.settings["exe_time"].append([int(self.app.info_text[1].get()), elapsedTime])
            self.save_settings()
            self.update_info()
            self.result_table = self.get_res_table(result_dictionary)
            PreviewKernel(self.result_table, meta_data)

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
        with open(self.sfile, 'w') as jsonfile:
            json.dump(self.settings, jsonfile)

    def cmd_max_cluster_updated(self, *args):
        print("CMD max_cluster_updated")
        if self.app.settings["max_clust"].get():
            val = self.app.settings["max_clust"].get()
            try:
                if int(val) > sum(self.app.col_map):
                    self.app.settings["max_clust"].set(str(sum(self.app.col_map)))
            except ValueError:
                self.app.settings["max_clust"].set(str(sum(self.app.col_map)))
            self.update_info()
    
    def cmd_min_cluster_updated(self, *args):
        print("CMD min_cluster_updated")
        if self.app.settings["min_clust"].get():
            val = self.app.settings["min_clust"].get()
            try:
                if int(val) > int(self.app.settings["max_clust"].get()):
                    self.app.settings["min_clust"].set(self.app.settings["max_clust"].get())
            except ValueError:
                self.app.settings["max_clust"].set("1")
            self.update_info()

    def get_age_filter(self):
        age_bitmap = ones(len(self.data))
        if self.age:
            try:
                min_age = int(self.app.settings["min_age"].get())
                max_age = int(self.app.settings["max_age"].get())
                age_bitmap = logical_and(array(self.age) >= min_age,
                                            array(self.age) <= max_age)
            except ValueError:
                pass
        elif self.app:
            self.app.settings["min_age"].set("N/A")
            self.app.settings["max_age"].set("N/A")
        return age_bitmap

    def get_sex_filter(self):
        if self.sex:
            try:
                sex_bitmap = zeros(len(self.data))
                sexes = self.get_vals(self.app.settings["sex"])
                for sex in sexes:
                    sex_bitmap = logical_or(sex_bitmap,
                                               array(self.sex) == sex)
                return sex_bitmap
            except ValueError:
                pass
        elif self.app:
            self.app.settings["sex"].set("N/A")
        return ones(len(self.data))

    def cmd_age_updated(self, *args):
        print("CMD cmd_age_updated")
        age_bitmap = self.get_age_filter()
        sex_bitmap = self.get_sex_filter()
        fan_bitmap = self.get_fan_filter()
        self.row_map = logical_and(age_bitmap, sex_bitmap)
        self.row_map = logical_and(self.row_map, fan_bitmap)
        if self.app:
            self.update_info()
        
    def get_fan_filter(self):
        fan_bitmap = ones(len(self.data))
        if self.ffan:
            fan_string = self.app.settings["ffan_var"].get()
            if fan_string == "All" or fan_string == "":
                fan_bitmap = ones(len(self.data))
            else:
                fan_bitmap = asarray(self.ffan[fan_string])
        return fan_bitmap
        

    def cmd_quit(self):
        print("CMD quit")
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
            self.app.info_text[2].set("{:d}".format(int(sum(self.row_map))))
            # Update estimated time using linear interpolation
            dat = array(self.settings["exe_time"])
            #def lin_extrapolate(self, x, y, point):
            exe_times = self.lin_extrapolate(dat[:,0], dat[:,1], combs)[0]
            str_time = self.to_str_time(exe_times, times=2)
            self.app.info_text[3].set(str_time)

    def to_str_time(self, seconds, times=1):
        if seconds < 0:
            return "Very fast"
        intervals = (
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )
        result = []
        ts = 0
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(int(value), name))
                ts += 1
                if ts >= times:
                    break
        if not result:
            return "{:0.2f}s".format(seconds)
        return ', '.join(result[:])

    def lin_extrapolate(self, x, y, point):
        x = array([x])
        x = concatenate((x, ones(shape(x))), axis=0).T
        y = array([y]).T
        m, c = linalg.lstsq(x, y)[0]
        return m*point + c

    def _bin_array(self, num, m):
        """Convert a positive integer num into an m-bit bit vector
        """
        return array(list(binary_repr(num).zfill(m))).astype(int8)
