from os.path import splitext
from tkinter import *

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from .reader_gui import ReaderGUI
import csv

class ReaderKernel(object):
    def __init__(self, parent, file_name):
        self.parent = parent
        self.file_name = file_name
        excel_formats = [".xlsx", ".xlsm", ".xltx", ".xltm"]
        _, file_extension = splitext(file_name)
        file_format = "csv"
        if file_extension in excel_formats:
            file_format = "excel"
        self.root = Tk()
        self.app = ReaderGUI(self.root, self, file_format)
        self.root.mainloop()
        self.root.destroy()
    
    def cmd_get_sheets(self):
        try:
            wb2 = load_workbook(self.file_name)
            return wb2.get_sheet_names()
        except InvalidFileException:
            return None

    def cmd_ok(self):
        if self.app.file_format.get() == "csv":
            with open(self.file_name) as csvfile:
                self.parent.data = list(csv.reader(csvfile, delimiter=self.app.delimiter.get()))
            self.parent.header = self.parent.data[int(self.app.header.get())-1]
            self.parent.data[0:int(self.app.header.get())] = []
            tmp_data = []
            err_rows = 0
            for row in self.parent.data:
                try:
                    tmp_data.append([int(j) for j in row])
                except ValueError:
                    err_rows += 1
            print(err_rows)
            for i, head in enumerate(self.parent.header):
                if head == "sex":
                    self.parent.sex = self.get_col(self.parent.data, i)
                    self.del_col(self.parent.data, i)
                elif head == "age":
                    self.parent.sex = self.get_col(self.parent.data, i)
                    self.del_col(self.parent.data, i)
            for i, _ in enumerate(self.parent.data):
                if not self.valid_col(self.get_col(self.parent.data, i)):
                    self.del_col(self.parent.data, i)
            self.root.quit()
        else:
            workbook = load_workbook(self.file_name)
            worksheet = workbook.get_sheet_by_name(self.app.sheet.get())
            self.parent.data = [[cell.value for cell in row] for row in worksheet.rows]
            try:
                self.parent.header = self.parent.data[int(self.app.header.get())-1]
                self.parent.data[0:int(self.app.header.get())] = []
            except ValueError:
                self.parent.header = self.parent.data.pop(0)
            self.root.quit()

    def valid_col(self, column):
        column = list(set(column))
        for value in range(1, 6):
            try:
                column.remove(value)
            except ValueError:
                pass
        if column:
            return False
        return True

    def del_col(self, data, col_idx):
        for row in data:
            del row[col_idx]

    def get_col(self, data, col_idx):
        return [row[col_idx] for row in data]

    def cmd_cancel(self):
        self.root.quit()