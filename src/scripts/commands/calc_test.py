import multiprocessing as mp

import numpy as np
from pkg_resources import resource_filename
from ..processes.bm_process import BM_Process


class CalcTest(object):
    def __init__(self, args):
        if not args["--data"]:
            args["--data"] = resource_filename("src.resources.example_data", "random_data_20_100.csv")
        
        self.raw_data = np.genfromtxt(args["--data"], delimiter=',')
        self.pos_bitm = self._map(self.raw_data, [4, 5])
        self.neg_bitm = self._map(self.raw_data, [1, 2])

        print(np.shape(self.pos_bitm))
        print(np.shape(self.neg_bitm))

        #np.set_printoptions(threshold=np.nan)
        #print(np.concatenate((self.raw_data, self.pos_bitm), axis=1))

    def run(self):
        nr_patterns = 2**np.shape(self.pos_bitm)[1]
        nr_cpu = mp.cpu_count()
        pattern_per_worker = int(nr_patterns / nr_cpu)
        workers = []
        score_queue = mp.Queue()
        pattern_queue = mp.Queue()
        
        start_pattern = 1
        end_pattern = pattern_per_worker
        for _ in range(nr_cpu):
            # Start of a new worker and add it to the list.
            bm = BM_Process(pos_bm=self.pos_bitm,
                            neg_bm=self.neg_bitm,
                            start=start_pattern,
                            end=end_pattern,
                            score_queue=score_queue,
                            pattern_queue=pattern_queue)
            bm.start()
            workers.append(bm)
            # Recalculate start and end pattern.
            start_pattern = end_pattern + 1
            end_pattern += pattern_per_worker
            if end_pattern > nr_patterns:
                end_pattern = nr_patterns
        for worker in workers:
            worker.join()

        score_mat = np.zeros((nr_cpu, np.shape(self.pos_bitm)[1]))
        pattern_mat = np.zeros((nr_cpu, np.shape(self.pos_bitm)[1]))
        i = 0
        while not score_queue.empty():
            score_mat[i][:] = score_queue.get()
            pattern_mat[i][:] = pattern_queue.get()
            i += 1
        score_vec = np.max(score_mat, axis=0)
        pattern_vec = np.array([pattern_mat[j][i]
                                for i, j in enumerate(np.argmax(score_mat, axis=0))])
        print(score_vec)
        print(pattern_vec)

    def _map(self, mat, map_list):
        bit_map = np.zeros(np.shape(mat))
        if isinstance(map_list, int):
            map_list = [map_list]
        for map_int in map_list:
            bit_map = np.logical_or(bit_map, mat==map_int)
        return bit_map
