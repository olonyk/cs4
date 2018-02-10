from tkinter import (BOTH, GROOVE, LEFT, Button, Checkbutton, E, Entry, Frame,
                     Grid, IntVar, Label, Menu, N, OptionMenu, S, StringVar, W,
                     X, Text, END, DISABLED)


class ReaderGUI(Frame):
    def __init__(self, master, kernel, file_format):
        self.kernel = kernel
        self.master = master
        master.title("Import")
        self.top_frame = Frame(master, width=400, height=200)
        self.top_frame.pack(fill=BOTH)
        self.master.resizable(width=False, height=False)

        self.file_format = StringVar(self.master)
        self.file_format.set(file_format)
        self.sheet = StringVar(self.master)
        self.delimiter = StringVar(self.master)
        self.delimiter.set(";")
        self.header = StringVar(self.master)
        self.header.set("1")

        self.sex_symb = StringVar(self.master)
        self.sex_symb.set("sex")
        self.age_symb = StringVar(self.master)
        self.age_symb.set("age")
        self.ffan_init = StringVar(self.master)
        self.ffan_init.set("x")

        choices = {"csv", "excel"}
 
        OptionMenu(self.top_frame, self.file_format, *choices, command=self.build_settings_frame).grid(row=0, column=0, sticky=W)
        self.settings_frame = Frame(self.top_frame)
        self.settings_frame.grid(row=1, column=0, sticky=W+E+N+S)
        self.build_settings_frame()

        frame = Frame(self.top_frame)
        frame.grid(row=2, column=0, sticky=E+W)
        Button(frame, text="OK", command=self.kernel.cmd_ok).grid(row=0, column=0, sticky=E)
        Button(frame, text="Cancel", command=self.kernel.cmd_cancel).grid(row=0, column=1, sticky=E)


    def build_settings_frame(self, *args):
        self.settings_frame.destroy()
        self.settings_frame = Frame(self.top_frame, width=400, height=100)
        self.settings_frame.grid(row=1, column=0, sticky=W+E+N+S)
        if self.file_format.get() == "csv":
            Label(self.settings_frame, text="Delimiter:").grid(row=0, column=0, sticky=W)
            Entry(self.settings_frame, textvariable=self.delimiter, width=1).grid(row=0, column=1, sticky=W)
            Label(self.settings_frame, text="Header row:").grid(row=1, column=0, sticky=W)
            Entry(self.settings_frame, textvariable=self.header, width=1).grid(row=1, column=1, sticky=W)
        else:
            sheets = self.kernel.cmd_get_sheets()
            if sheets:
                self.sheet.set(sheets[0])
                Label(self.settings_frame, text="Data sheet:").grid(row=0, column=0, sticky=W)
                OptionMenu(self.settings_frame, self.sheet, *sheets).grid(row=0, column=1, sticky=W)
                Label(self.settings_frame, text="Header row:").grid(row=1, column=0, sticky=W)
                Entry(self.settings_frame, textvariable=self.header, width=1).grid(row=1, column=1, sticky=W)
                Label(self.settings_frame, text="Gender header:").grid(row=2, column=0, sticky=W)
                Entry(self.settings_frame, textvariable=self.sex_symb, width=5).grid(row=2, column=1, sticky=W)
                Label(self.settings_frame, text="Age header:").grid(row=3, column=0, sticky=W)
                Entry(self.settings_frame, textvariable=self.age_symb, width=5).grid(row=3, column=1, sticky=W)
                Label(self.settings_frame, text="Format fan initial:").grid(row=4, column=0, sticky=W)
                Entry(self.settings_frame, textvariable=self.ffan_init, width=5).grid(row=4, column=1, sticky=W)
            else:
                T = Text(self.settings_frame, height=3, width=30)
                T.grid(row=0, column=0, sticky=W)
                T.insert(END, "Unable to load as Workbook\nSupported formats are: .xlsx, .xlsm, .xltx and .xltm")
                T.config(state=DISABLED)
