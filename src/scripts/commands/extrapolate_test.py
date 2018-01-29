import json
from pkg_resources import resource_filename
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

class ExtrapolateTest(object):
    def __init__(self, args):
        self.settings = json.load(open(resource_filename("src.resources.settings",
                                                         "settings.json")))
        exe_time = np.sort(np.array(self.settings["exe_time"]), axis=0)
        x_time = exe_time[:,0]
        y_time = exe_time[:,1]
        plt.plot(x_time, y_time, 'ro')

        x_inter = np.arange(100,2048575,100000)
        y_inter = np.interp(x_inter, x_time, y_time)

        plt.plot(x_inter, y_inter, 'gx')

        # Own linear extrapolation
        x_time = np.array([x_time])
        x_time = np.concatenate((x_time, np.ones(np.shape(x_time))), axis=0).T
        y_time = np.array([y_time]).T
        print(np.shape(x_time), np.shape(y_time))
        m, c = np.linalg.lstsq(x_time, y_time)[0]
        print(m, c)
        plt.plot(x_inter, m*x_inter + c, "bx")
        plt.show()

    def run(self):
        pass
    def lin_extrapolate(self, x, y, point):
        x = np.array([x])
        x = np.concatenate((x, np.ones(np.shape(x))), axis=0).T
        y = np.array([y]).T
        m, c = np.linalg.lstsq(x, y)[0]
        return m*point + c

class IterTest(object):
    def __init__(self, args):
        #self.naive_test()
        saves = []
        fills = []
        for fill in range(20):
            fills.append(fill)
            saves.append(self.exp_1(fill))
        plt.plot(fills, saves)
        plt.show()
    
    def exp_1(self, fill):
        lim = 3
        size_ok = []
        rints_ok = []
        size_no = []
        rints_no = []
        sizes = []
        rints = []

        c_list = [0]
        iterations = 0
        for x in range(fill-1):
            for c_i, c_v in enumerate(c_list):
                run_int = (2**x)+c_v
                run_bin, size = self.cast_to_bin(run_int, fill)

                rints.append(run_int)
                sizes.append(size)
                
                iterations += 1

                mark = ""
                if size > lim:
                    c_list.pop(c_i)
                    mark = "<="
                    size_no.append(size)
                    rints_no.append(run_int)
                    continue
                else:
                    size_ok.append(size)
                    rints_ok.append(run_int)

                #print("{}\t{}\t{}\t2^{} + {}\t{}".format(run_int, run_bin, size, x, c_v, mark))
            #print(c_list)
            c_list = c_list + list(range(c_list[-1]+1, 2**x -1))
        return iterations / (float(2**(fill-1)))
    
    def naive_test(self):
        fill = 8
        lim = 3
        size_ok = []
        rints_ok = []
        size_no = []
        rints_no = []
        sizes = []
        rints = []
        for x in range(fill-1):
            c = 0
            while c < 2**x:
                run_int = (2**x)+c
                run_bin, size = self.cast_to_bin(run_int, fill)

                rints.append(run_int)
                sizes.append(size)

                mark = ""
                if size > lim:
                    mark = "<="
                    size_no.append(size)
                    rints_no.append(run_int)
                else:
                    size_ok.append(size)
                    rints_ok.append(run_int)

                print("{}\t{}\t{}\t2^{} + {}\t{}".format(run_int, run_bin, size, x, c, mark))
                c += 1
        plt.plot(rints_no, size_no, 'ro')
        plt.plot(rints_ok, size_ok, 'go')
        plt.plot(rints, sizes)
        plt.show()
        
    
    def cast_to_bin(self, an_int, fill):
        bin_list_int = list(bin(an_int))[2:]
        size = bin_list_int.count("1")
        bin_list_int = ["0"]*(fill-len(bin_list_int)) + bin_list_int
        return ",".join(bin_list_int), size

    def run(self):
        pass
