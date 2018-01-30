from .preview_gui import PreviewGUI
import tkinter as tk
from .export_kernel import ExportKernel
from tkinter.filedialog import asksaveasfilename

class PreviewKernel(object):
    def __init__(self, data_table, meta_data):
        self.data_table = data_table
        self.root = tk.Tk()
        self.app = PreviewGUI(self.root, self, data_table, meta_data)
        self.root.mainloop()
        self.root.destroy()

    def cmd_export(self):
        if self.data_table:
            file_name = asksaveasfilename(defaultextension=".xlsx")
            if file_name is None: # asksaveasfile return `None` if dialog closed with "cancel".
                return
            ExportKernel(self, self.data_table, file_name)