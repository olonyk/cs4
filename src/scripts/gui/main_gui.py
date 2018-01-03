from tkinter import *
from ..support.widgets import ScrollableFrame

class MainGUI(Frame):
    def __init__(self, master, kernel):
        self.kernel = kernel
        self.master = master
        self.top_frame = Frame(master)
        self.top_frame.pack(fill=BOTH, expand=True)
        self.top_frame.columnconfigure(1, weight=1)
        Grid.rowconfigure(self.top_frame, 0, weight=1)

        # Variables
        self.include_cols = []
        self.col_map = []
        self.settings = {}

        # Settings frame
        self.build_settings_frame()

        # Info frame
        self.build_info_frame()
        
        # Menu bar
        self.build_menue_bar()

        # Overview frame
        self.overview_frame = Frame(self.top_frame, bd=1, relief=GROOVE)
        self.overview_frame.grid(row=0, column=1, rowspan=2, sticky=W+E+N+S)
    
    def build_overview(self, data, header):
        self.overview_frame.destroy()
        self.overview_frame = Frame(self.top_frame, bd=1, relief=GROOVE)
        self.overview_frame.grid(row=0, column=1, rowspan=2, sticky=W+E+N+S)
        
        self.overview_frame.columnconfigure(0, weight=1)
        self.overview_frame.rowconfigure(0, weight=1)

        win_frame = Frame(self.overview_frame)
        x_frame = Frame(self.overview_frame)
        y_frame = Frame(self.overview_frame)
        z_frame = Frame(self.overview_frame)

        win_frame.grid(row=0, column=0, sticky=W+E+N+S)
        x_frame.grid(row=1, column=0, sticky=W+E)
        y_frame.grid(row=0, column=1, sticky=N+S)
        z_frame.grid(row=1, column=1, sticky=W+E+N+S)

        scroll_frame = ScrollableFrame(win_frame, x_frame, y_frame)
        if header:
            column_frames = []
            self.include_cols = []
            for i, genre in enumerate(header):
                frame = Frame(scroll_frame, bd=1, relief=GROOVE)
                frame.pack(side=LEFT, padx=1, fill=X, expand=False)
                column_frames.append(frame)
                var = IntVar(self.master)
                var.set(1)
                self.include_cols.append(var)
                Checkbutton(frame, text=str(genre),
                            variable=var,
                            command=lambda: self.toggle_col(column_frames)).pack()
                #for row in data:
                #    Label(frame, text=str(row[i])).pack()
            self.settings["max_clust"].set(str(len(header)))
        self.toggle_col(column_frames)

    def toggle_col(self, column_frames):
        self.col_map = [var.get() for var in self.include_cols]
        if int(self.settings["max_clust"].get()) > sum(self.col_map):
            self.settings["max_clust"].set(str(sum(self.col_map)))
        for on, column_frame in zip(self.col_map, column_frames):
            for widget in column_frame.winfo_children():
                if on and not isinstance(widget, Checkbutton):
                    widget.config(state="normal")
                elif not isinstance(widget, Checkbutton):
                    widget.config(state=DISABLED)
        self.kernel.update_info()

    def build_menue_bar(self):
        menubar = Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import...", command=self.kernel.cmd_import)
        filemenu.add_command(label="Export...", command=self.kernel.cmd_export)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)

    def build_settings_frame(self):
        frame = Frame(self.top_frame, bd=1, relief=GROOVE)
        frame.grid(row=0, column=0, sticky=W+E+N+S)

        self.settings = {"pos_val": StringVar(self.master),
                         "neg_val": StringVar(self.master),
                         "max_clust": StringVar(self.master),
                         "min_clust": StringVar(self.master),
                         "max_age": StringVar(self.master),
                         "min_age": StringVar(self.master),
                         "sex": StringVar(self.master)}
        self.settings["pos_val"].set("4 5")
        self.settings["neg_val"].set("1 2")
        self.settings["max_clust"].set("0")
        self.settings["max_clust"].trace("w", self.kernel.cmd_max_cluster_updated)
        self.settings["min_clust"].set("0")
        self.settings["max_age"].set("0")
        self.settings["min_age"].set("0")
        self.settings["sex"].set("1 2")

        lbls = ["Positive values:",
                "Negative values:",
                "Maximum cluster size:",
                "Minimum cluster size:",
                "Maximum age:",
                "Minimum age:",
                "Sex:"]
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

        Button(frame, text="Execute", command=self.kernel.cmd_execute).grid(row=100,
                                                                            column=0,
                                                                            sticky=W)

    def build_info_frame(self):
        info_frame = Frame(self.top_frame, bd=1, relief=GROOVE)
        info_frame.grid(row=1, column=0, sticky=W+E+N+S)
        Label(info_frame, text="Number of columns:").grid(row=0, column=0, sticky=W)
        Label(info_frame, text="Number of combinations:").grid(row=1, column=0, sticky=W)
        Label(info_frame, text="Estimated time:").grid(row=2, column=0, sticky=W)

        self.info_text = [StringVar(), StringVar(), StringVar()]
        for i, str_var in enumerate(self.info_text):
            str_var.set("N/A")
            Label(info_frame, textvariable=str_var).grid(row=i, column=1, sticky=W)
