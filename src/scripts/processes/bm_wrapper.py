import multiprocessing as mp
from copy import deepcopy

from numpy import zeros, shape, logical_or, argmax, array
from numpy import max as npmax

from .bm_process import BM_Process


class BM_Wrapper(object):
    def analyse(self, max_cluster=None, data=None, pos_map=None, neg_map=None):
        pos_bitm = self._map(data, pos_map)
        neg_bitm = self._map(data, neg_map)
        result_queue = mp.Queue()
        workmanager = BM_WrapperProcess(result_queue, max_cluster, pos_bitm, neg_bitm)
        workmanager.start()
        workmanager.join()
        return result_queue.get()

    def _map(self, mat, map_list):
        bit_map = zeros(shape(mat))
        if isinstance(map_list, int):
            map_list = [map_list]
        for map_int in map_list:
            bit_map = logical_or(bit_map, mat==map_int)
        return bit_map

class BM_WrapperProcess(mp.Process):
    def __init__(self, result_queue, max_cluster, pos_bitm, neg_bitm):
        super(BM_WrapperProcess, self).__init__()
        self.pos_bitm = pos_bitm
        self.neg_bitm = neg_bitm
        self.result_queue = result_queue
        self.process = None
        self.workers = []
        self.max_cluster = shape(self.pos_bitm)[1]
        if max_cluster:
            self.max_cluster = deepcopy(max_cluster)

    def run(self):
        nr_cpu = mp.cpu_count()
        nr_patterns = 2**shape(self.pos_bitm)[1]
        pattern_per_worker = int(nr_patterns / nr_cpu)
        self.workers = []
        score_queue = mp.Queue()
        pattern_queue = mp.Queue()
        start_pattern = 1
        end_pattern = pattern_per_worker
        # If the data is large enough spread it out on different cpu:s, if not just start one
        # worker.
        if pattern_per_worker > 1:
            for _ in range(nr_cpu):
                # Start of a new worker and add it to the list.
                worker = BM_Process(pos_bm=self.pos_bitm,
                                    neg_bm=self.neg_bitm,
                                    start=start_pattern,
                                    end=end_pattern,
                                    score_queue=score_queue,
                                    pattern_queue=pattern_queue,
                                    max_cluster=self.max_cluster)
                worker.start()
                self.workers.append(worker)
                # Recalculate start and end pattern.
                start_pattern = end_pattern + 1
                end_pattern += pattern_per_worker
                if end_pattern > nr_patterns:
                    end_pattern = nr_patterns
        else:
            # Start of a new worker and add it to the list.
            worker = BM_Process(pos_bm=self.pos_bitm,
                                neg_bm=self.neg_bitm,
                                start=1,
                                end=nr_patterns,
                                score_queue=score_queue,
                                pattern_queue=pattern_queue,
                                max_cluster=self.max_cluster)
            worker.start()
            self.workers.append(worker)

        for worker in self.workers:
            worker.join()

        score_mat = zeros((nr_cpu, shape(self.pos_bitm)[1]))
        pos_mat = zeros((nr_cpu, shape(self.pos_bitm)[1]))
        neg_mat = zeros((nr_cpu, shape(self.pos_bitm)[1]))
        pattern_mat = zeros((nr_cpu, shape(self.pos_bitm)[1]))
        i = 0
        while not score_queue.empty():
            score_post = score_queue.get()
            score_mat[i][:] = score_post["score"]
            pattern_mat[i][:] = score_post["pattern"]
            pos_mat[i][:] = score_post["pos"]
            neg_mat[i][:] = score_post["neg"]
            i += 1
        score_vec = npmax(score_mat, axis=0)
        pattern_vec = array([pattern_mat[j][i]
                                for i, j in enumerate(argmax(score_mat, axis=0))])
        neg_vec = array([neg_mat[j][i] for i, j in enumerate(argmax(score_mat, axis=0))])
        pos_vec = array([pos_mat[j][i] for i, j in enumerate(argmax(score_mat, axis=0))])
        self.result_queue.put({"score_vec":score_vec,
                               "pattern_vec":pattern_vec,
                               "pos_vec":pos_vec,
                               "neg_vec":neg_vec})
        return
