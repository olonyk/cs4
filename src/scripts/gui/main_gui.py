from tkinter import (GROOVE, LEFT, Button, Checkbutton, E, Entry, Frame, Grid,
                     IntVar, Label, Menu, N, OptionMenu, S, StringVar, W)

from numpy import array, binary_repr, int8

from ..support.widgets import ScrollableFrame


class MainGUI(Frame):
    def __init__(self, master, kernel):
        self.kernel = kernel
        self.master = master
        
        self.master.columnconfigure(1, weight=1)
        Grid.rowconfigure(self.master, 0, weight=1)

        self.left_frame = Frame(master)
        self.left_frame.grid(row=0, column=0, sticky=W+E+N+S)
        self.left_frame.columnconfigure(1, weight=1)
        Grid.rowconfigure(self.left_frame, 0, weight=1)

        self.right_frame = Frame(master)
        self.right_frame.grid(row=0, column=1, sticky=W+E+N+S)
        self.right_frame.columnconfigure(1, weight=1)
        Grid.rowconfigure(self.right_frame, 1, weight=1)

        # Variables
        self.include_cols = []
        self.col_map = []
        self.settings = {}
        self.om = None

        # Settings frame
        self.build_settings_frame()

        # Info frame
        self.build_info_frame()
        
        # Menu bar
        self.build_menue_bar()

        # Overview frame
        self.overview_frame = Frame(self.right_frame, bd=1, relief=GROOVE)
        self.overview_frame.grid(row=0, column=1, rowspan=2, sticky=W+E+N+S)
    
    def build_overview(self, data, header):
        self.overview_frame.destroy()
        self.overview_frame = Frame(self.right_frame, bd=1, relief=GROOVE)
        self.overview_frame.grid(row=0, column=1, rowspan=2, sticky=W+E+N+S)
        
        self.overview_frame.columnconfigure(0, weight=1)
        self.overview_frame.rowconfigure(0, weight=1)

        win_frame = Frame(self.overview_frame, background="#ffffff")
        x_frame = Frame(self.overview_frame)
        y_frame = Frame(self.overview_frame)
        z_frame = Frame(self.overview_frame)

        win_frame.grid(row=0, column=0, sticky=W+E+N+S)
        x_frame.grid(row=1, column=0, sticky=W+E)
        y_frame.grid(row=0, column=1, sticky=N+S)
        z_frame.grid(row=1, column=1, sticky=W+E+N+S)

        scroll_frame = ScrollableFrame(win_frame, x_frame, y_frame)
        if header:
            self.include_cols = []
            for i, genre in enumerate(header):
                var = IntVar(self.master)
                var.set(1)
                self.include_cols.append(var)
                Checkbutton(scroll_frame,
                               text=str(genre),
                               justify=LEFT,
                               anchor=W,
                               variable=var,
                               command=lambda: self.toggle_col()).grid(row=i, column=0, sticky=W+E)
            self.col_map = [var.get() for var in self.include_cols]
            self.settings["max_clust"].set(str(len(header)))
        self.toggle_col()

    def toggle_col(self):
        self.col_map = [var.get() for var in self.include_cols]
        if int(self.settings["max_clust"].get()) > sum(self.col_map):
            self.settings["max_clust"].set(str(sum(self.col_map)))
        self.kernel.update_info()

    def build_menue_bar(self):
        menubar = Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import...", command=self.kernel.cmd_import)
        filemenu.add_command(label="Export...", command=self.kernel.cmd_export)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.kernel.cmd_quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)

    def build_settings_frame(self):
        frame = Frame(self.left_frame, bd=1, relief=GROOVE)
        frame.grid(row=0, column=0, sticky=W+E+N+S)

        self.settings = {"pos_val": StringVar(self.master),
                         "neg_val": StringVar(self.master),
                         "max_clust": StringVar(self.master),
                         "min_clust": StringVar(self.master),
                         "max_age": StringVar(self.master),
                         "min_age": StringVar(self.master),
                         "sex": StringVar(self.master),
                         "ffan_var": StringVar(self.master),
                         "ffan_list": []}
        self.settings["pos_val"].set("5")
        self.settings["neg_val"].set("1 2")
        self.settings["max_clust"].set("0")
        self.settings["max_clust"].trace("w", self.kernel.cmd_max_cluster_updated)
        self.settings["min_clust"].set("1")
        self.settings["min_clust"].trace("w", self.kernel.cmd_min_cluster_updated)
        self.settings["max_age"].set("0")
        self.settings["max_age"].trace("w", self.kernel.cmd_age_updated)
        self.settings["min_age"].set("0")
        self.settings["min_age"].trace("w", self.kernel.cmd_age_updated)
        self.settings["sex"].set("1 2")
        self.settings["sex"].trace("w", self.kernel.cmd_age_updated)
        self.settings["ffan_var"].set("All")
        self.settings["ffan_var"].trace("w", self.kernel.cmd_age_updated)

        lbls = ["Positive values:",
                "Negative values:",
                "Maximum cluster size:",
                "Minimum cluster size:",
                "Maximum age:",
                "Minimum age:",
                "Sex:",
                "Format fan:"]
        for i, lbl_text in enumerate(lbls):
            Label(frame, text=lbl_text).grid(row=i, column=0, sticky=W)
        lbls = ["pos_val",
                "neg_val",
                "max_clust",
                "min_clust",
                "max_age",
                "min_age",
                "sex"]
        for i, lbl_text in enumerate(lbls):
            Entry(frame, textvariable=self.settings[lbl_text], width=4).grid(row=i,
                                                                                column=1,
                                                                                sticky=W)
        # TODO Add format fan handle.
        self.om = OptionMenu(frame, self.settings["ffan_var"], self.settings["ffan_list"])
        self.om.grid(row=i+1, column=1, sticky=W)

        Button(frame, text="Execute", command=self.kernel.cmd_execute).grid(row=100,
                                                                            column=0,
                                                                            sticky=W)
        self.kernel.default_settings(app=self)

    def update_ffan(self):
        if self.om:
            menu = self.om["menu"]
            menu.delete(0, "end")
            for string in self.settings["ffan_list"]:
                print(string)
                menu.add_command(label=string, 
                                 command=lambda value=string: self.settings["ffan_var"].set(value))

    def build_info_frame(self):
        info_frame = Frame(self.left_frame, bd=1, relief=GROOVE)
        info_frame.grid(row=1, column=0, sticky=W+E+N+S)
        Label(info_frame, text="Number of columns:").grid(row=0, column=0, sticky=W)
        Label(info_frame, text="Number of combinations:").grid(row=1, column=0, sticky=W)
        Label(info_frame, text="Number of participants:").grid(row=2, column=0, sticky=W)
        Label(info_frame, text="Estimated time:").grid(row=3, column=0, sticky=W)

        self.info_text = [StringVar(), StringVar(), StringVar(), StringVar()]
        for i, str_var in enumerate(self.info_text):
            str_var.set("N/A")
            Label(info_frame, textvariable=str_var).grid(row=i, column=1, sticky=W)

    def _bin_array(self, num, m):
        """Convert a positive integer num into an m-bit bit vector
        """
        return array(list(binary_repr(num).zfill(m))).astype(int8)
