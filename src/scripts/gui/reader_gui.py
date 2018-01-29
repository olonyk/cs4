import tkinter as tk


class ReaderGUI(tk.Frame):
    def __init__(self, master, kernel, file_format):
        self.kernel = kernel
        self.master = master
        self.top_frame = tk.Frame(master, width=400, height=200)
        self.top_frame.pack(fill=tk.BOTH)
        self.master.resizable(width=False, height=False)

        self.file_format = tk.StringVar(self.master)
        self.file_format.set(file_format)
        self.sheet = tk.StringVar(self.master)
        self.delimiter = tk.StringVar(self.master)
        self.delimiter.set(";")
        self.header = tk.StringVar(self.master)
        self.header.set("1")

        self.sex_symb = tk.StringVar(self.master)
        self.sex_symb.set("sex")
        self.age_symb = tk.StringVar(self.master)
        self.age_symb.set("age")

        choices = {"csv", "excel"}
 
        tk.OptionMenu(self.top_frame, self.file_format, *choices, command=self.build_settings_frame).grid(row=0, column=0, sticky=tk.W)
        self.settings_frame = tk.Frame(self.top_frame)
        self.settings_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.build_settings_frame()

        frame = tk.Frame(self.top_frame)
        frame.grid(row=2, column=0, sticky=tk.E+tk.W)
        tk.Button(frame, text="OK", command=self.kernel.cmd_ok).grid(row=0, column=0, sticky=tk.E)
        tk.Button(frame, text="Cancel", command=self.kernel.cmd_cancel).grid(row=0, column=1, sticky=tk.E)


    def build_settings_frame(self, *args):
        self.settings_frame.destroy()
        self.settings_frame = tk.Frame(self.top_frame, width=400, height=100)
        self.settings_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        if self.file_format.get() == "csv":
            tk.Label(self.settings_frame, text="Delimiter:").grid(row=0, column=0, sticky=tk.W)
            tk.Entry(self.settings_frame, textvariable=self.delimiter, width=1).grid(row=0, column=1, sticky=tk.W)
            tk.Label(self.settings_frame, text="Header row:").grid(row=1, column=0, sticky=tk.W)
            tk.Entry(self.settings_frame, textvariable=self.header, width=1).grid(row=1, column=1, sticky=tk.W)
        else:
            sheets = self.kernel.cmd_get_sheets()
            if sheets:
                self.sheet.set(sheets[0])
                tk.Label(self.settings_frame, text="Data sheet:").grid(row=0, column=0, sticky=tk.W)
                tk.OptionMenu(self.settings_frame, self.sheet, *sheets).grid(row=0, column=1, sticky=tk.W)
                tk.Label(self.settings_frame, text="Header row:").grid(row=1, column=0, sticky=tk.W)
                tk.Entry(self.settings_frame, textvariable=self.header, width=1).grid(row=1, column=1, sticky=tk.W)
                tk.Label(self.settings_frame, text="Sex header:").grid(row=2, column=0, sticky=tk.W)
                tk.Entry(self.settings_frame, textvariable=self.sex_symb, width=5).grid(row=2, column=1, sticky=tk.W)
                tk.Label(self.settings_frame, text="Age header:").grid(row=3, column=0, sticky=tk.W)
                tk.Entry(self.settings_frame, textvariable=self.age_symb, width=5).grid(row=3, column=1, sticky=tk.W)
            else:
                T = tk.Text(self.settings_frame, height=3, width=30)
                T.grid(row=0, column=0, sticky=tk.W)
                T.insert(tk.END, "Unable to load as Workbook\nSupported formats are: .xlsx, .xlsm, .xltx and .xltm")
                T.config(state=tk.DISABLED)
