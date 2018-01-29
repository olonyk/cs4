import numpy as np

class LinAlg(object):
    def lin_extrapolate(self, x, y, point):
        x = np.array([x])
        x = np.concatenate((x, np.ones(np.shape(x))), axis=0).T
        y = np.array([y]).T
        m, c = np.linalg.lstsq(x, y)[0]
        return m*point + c