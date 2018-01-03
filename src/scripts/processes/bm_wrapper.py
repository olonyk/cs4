import multiprocessing as mp

import numpy as np

from .bm_process import BM_Process


class BM_Wrapper(object):
    def analyse(self, caller=None, data=None, pos_map=None, neg_map=None):
        pos_bitm = self._map(data, pos_map)
        neg_bitm = self._map(data, neg_map)
        result_queue = mp.Queue()
        workmanager = BM_WrapperProcess(result_queue, pos_bitm, neg_bitm)
        workmanager.start()
        workmanager.join()
        result = result_queue.get()
        score_vec = result["score_vec"]
        pattern_vec = result["pattern_vec"]
        return score_vec, pattern_vec

    def _map(self, mat, map_list):
        bit_map = np.zeros(np.shape(mat))
        if isinstance(map_list, int):
            map_list = [map_list]
        for map_int in map_list:
            bit_map = np.logical_or(bit_map, mat==map_int)
        return bit_map

class BM_WrapperProcess(mp.Process):
    def __init__(self, result_queue, pos_bitm, neg_bitm):
        super(BM_WrapperProcess, self).__init__()
        self.pos_bitm = pos_bitm
        self.neg_bitm = neg_bitm
        self.result_queue = result_queue
        self.process = None
        self.workers = []

    def run(self):
        nr_cpu = mp.cpu_count()
        nr_patterns = 2**np.shape(self.pos_bitm)[1]
        pattern_per_worker = int(nr_patterns / nr_cpu)
        self.workers = []
        score_queue = mp.Queue()
        pattern_queue = mp.Queue()
        
        start_pattern = 1
        end_pattern = pattern_per_worker
        for _ in range(nr_cpu):
            # Start of a new worker and add it to the list.
            worker = BM_Process(pos_bm=self.pos_bitm,
                                neg_bm=self.neg_bitm,
                                start=start_pattern,
                                end=end_pattern,
                                score_queue=score_queue,
                                pattern_queue=pattern_queue)
            worker.start()
            self.workers.append(worker)
            # Recalculate start and end pattern.
            start_pattern = end_pattern + 1
            end_pattern += pattern_per_worker
            if end_pattern > nr_patterns:
                end_pattern = nr_patterns

        for worker in self.workers:
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
        self.result_queue.put({"score_vec":score_vec, "pattern_vec":pattern_vec})
        return score_vec, pattern_vec

