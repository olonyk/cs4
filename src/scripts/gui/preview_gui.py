import matplotlib
matplotlib.use('TkAgg')

from tkinter import (GROOVE, LEFT, Button, Checkbutton, E, Entry, Frame, Grid,
                     IntVar, Label, Menu, N, OptionMenu, S, StringVar, W, TOP, BOTH)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from ..support.widgets import ScrollableFrame

class PreviewGUI(Frame):
    def __init__(self, master, kernel, data_table, meta_data):
        self.kernel = kernel
        self.master = master

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        win_frame = Frame(master)
        x_frame = Frame(master)
        y_frame = Frame(master)
        z_frame = Frame(master)

        win_frame.grid(row=0, column=0, sticky=W+E+N+S)
        x_frame.grid(row=1, column=0, sticky=W+E)
        y_frame.grid(row=0, column=1, sticky=N+S)
        z_frame.grid(row=1, column=1, sticky=W+E+N+S)

        self.top_frame = ScrollableFrame(win_frame, x_frame, y_frame)
        self.top_frame.columnconfigure(1, weight=1)

        self.lbl_table = []

        graph_frame = self.build_graph_frame(data_table, meta_data)
        graph_frame.grid(row=0, column=1, sticky=W+E+N+S)

        table_frame = self.build_table_frame(data_table, meta_data)
        table_frame.grid(row=1, columnspan=2, column=0, sticky=W+E+N+S)

        meta_frame = self.build_meta_data_frame(data_table, meta_data)
        meta_frame.grid(row=0, column=0, sticky=W+E+N+S)

    def build_graph_frame(self, data_table, meta_data):
        graph_frame = Frame(self.top_frame, relief=GROOVE, bd=1)

        pts_tot = data_table[-1][1::]
        x_range = arange(meta_data["min_clust"], meta_data["max_clust"]+1, 1.0)
        fig = Figure(figsize=(5, 3), dpi=100)
        sub_fig = fig.add_subplot(111)
        sub_fig.fill_between(x_range, 0, pts_tot)

        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        return graph_frame
    
    def build_table_frame(self, data_table, meta_data):
        table_frame = Frame(self.top_frame, relief=GROOVE, bd=1)
        data_table = self.sort_data_table(data_table)
        self.lbl_table = []
        for r, row in enumerate(data_table):
            lbl_row = []
            for c, col in enumerate(row):
                lbl = Label(table_frame, text=col, justify=LEFT, anchor=W)
                lbl.grid(row=r, column=c, sticky=W+E+N+S)
                if r > 0 and r < len(data_table)-3 and not col == "":
                    lbl.bind("<Enter>", lambda event, text=col: self.enter_widget(text))
                    lbl.bind("<Leave>", lambda event, text=col: self.leave_widget(text))
                    lbl_row.append(lbl)
            self.lbl_table.append(lbl_row)
        return table_frame

    def enter_widget(self, text):
        for lbl_row in self.lbl_table:
            for lbl in lbl_row:
                if lbl["text"] == text:
                    lbl.configure(bg="green")
    
    def leave_widget(self, text):
        for lbl_row in self.lbl_table:
            for lbl in lbl_row:
                if lbl["text"] == text:
                    lbl.configure(bg="white")

    def sort_data_table(self, data_table):
        # Transpose the table.
        data_table = list(map(list, zip(*data_table)))
        # Iterate over rows (previously columns).
        prev_row = []
        for row in data_table:
            for col_i, col in enumerate(prev_row):
                if col == "" or isinstance(col, int):
                    continue
                elif prev_row:
                    try:
                        row[row.index(col)], row[col_i] = row[col_i], row[row.index(col)]
                    except ValueError:
                        continue
            prev_row = row
        # Transpose the table back.
        return list(map(list, zip(*data_table)))
    
    def build_meta_data_frame(self, data_table, meta_data):
        meta_frame = Frame(self.top_frame, relief=GROOVE, bd=1)

        Label(meta_frame, text="Positiv values:", justify=LEFT, anchor=W).grid(row=0, column=0, sticky=W+E+N+S)
        Label(meta_frame, text=meta_data["pos_val"], justify=LEFT, anchor=W).grid(row=0, column=1, sticky=W+E+N+S)

        Label(meta_frame, text="Negativ values:", justify=LEFT, anchor=W).grid(row=1, column=0, sticky=W+E+N+S)
        Label(meta_frame, text=meta_data["neg_val"], justify=LEFT, anchor=W).grid(row=1, column=1, sticky=W+E+N+S)

        Label(meta_frame, text="Largest cluster:", justify=LEFT, anchor=W).grid(row=2, column=0, sticky=W+E+N+S)
        Label(meta_frame, text=meta_data["max_clust"], justify=LEFT, anchor=W).grid(row=2, column=1, sticky=W+E+N+S)

        Label(meta_frame, text="Smallest cluster:", justify=LEFT, anchor=W).grid(row=3, column=0, sticky=W+E+N+S)
        Label(meta_frame, text=meta_data["min_clust"], justify=LEFT, anchor=W).grid(row=3, column=1, sticky=W+E+N+S)
        
        Label(meta_frame, text="Format fans:", justify=LEFT, anchor=W).grid(row=4, column=0, sticky=W+E+N+S)
        Label(meta_frame, text=meta_data["ffan"], justify=LEFT, anchor=W).grid(row=4, column=1, sticky=W+E+N+S)

        Label(meta_frame, text="Running time:", justify=LEFT, anchor=W).grid(row=5, column=0, sticky=W+E+N+S)
        Label(meta_frame, text=meta_data["elapsedTime"], justify=LEFT, anchor=W).grid(row=5, column=1, sticky=W+E+S)

        max_pts = max(data_table[-1][1::])
        max_cls = data_table[0][data_table[-1].index(max_pts)]

        Label(meta_frame, text="Best cluster size:", justify=LEFT, anchor=W).grid(row=6, column=0, sticky=W+E+N+S)
        Label(meta_frame, text=max_cls, justify=LEFT, anchor=W).grid(row=6, column=1, sticky=W+E+N+S)

        Label(meta_frame, text="Best cluster points:", justify=LEFT, anchor=W).grid(row=7, column=0, sticky=W+E+N+S)
        Label(meta_frame, text=str(max_pts), justify=LEFT, anchor=W).grid(row=7, column=1, sticky=W+E+N+S)
        
        Button(meta_frame, text="Export", command=lambda:self.kernel.cmd_export()).grid(row=100, column=0, sticky=W+E+N+S)
        return meta_frame
