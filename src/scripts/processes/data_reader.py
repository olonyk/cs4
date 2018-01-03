from os.path import splitext

class DataReader(object):
    def read_any(self, file_name):
        csv_formats = [".csv", ".txt"]
        excel_formats = [".xlsx", ".xlsm", ".xls"]
        _, file_extension = splitext(file_name)
        if file_extension in csv_formats:
            ReadCSVKernel(file_name)
            return 

        with open(file_name) as import_file:
            data = import_file.readlines()
        return data