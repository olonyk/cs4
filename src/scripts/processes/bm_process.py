from multiprocessing import Process
from numpy import inf, ones, shape, array, binary_repr, int8, zeros
from numpy import sum as npsum
from numpy import any as npany

class BM_Process(Process):
    def __init__(self, **kwargs):
        super(BM_Process, self).__init__()

        self.pos_bm=kwargs["pos_bm"]
        self.neg_bm=kwargs["neg_bm"]
        self._start=1
        self._m = 2**shape(self.pos_bm)[1]
        self._end= self._m
        self._score_mat = None

        if "start" in kwargs.keys():
            self._start = kwargs["start"]
        if "end" in kwargs.keys():
            self._end = kwargs["end"]
        if "score_queue" in kwargs.keys():
            self._score_queue = kwargs["score_queue"]
            self._pattern_queue = kwargs["pattern_queue"]
        self.max_cluster = kwargs["max_cluster"]

    def run(self):
        _, cols = shape(self.pos_bm)
        top_scores = ones(cols)*-inf
        top_pos = ones(cols)*-inf
        top_neg = ones(cols)*-inf
        top_pattern = zeros(cols)
        for running_int in range(self._start, self._end):
            col_pattern = self._bin_array(running_int, cols)
            if npsum(col_pattern) > self.max_cluster:
                continue
            pos_score = npany(self.pos_bm * col_pattern, axis=1)
            neg_score = npany(self.neg_bm * col_pattern, axis=1)
            pattern_score = npsum(pos_score) - npsum(neg_score)
            if pattern_score > top_scores[sum(col_pattern)-1]:
                top_scores[sum(col_pattern)-1] = pattern_score
                top_pattern[sum(col_pattern)-1] = running_int
                top_pos[sum(col_pattern)-1] = npsum(pos_score)
                top_neg[sum(col_pattern)-1] = npsum(neg_score)
            if running_int % 10000 == 0:
                print((running_int - self._start)/(self._end - self._start))
        # Write the result to the score and pattern matrices.
        if self._score_queue:
            self._score_queue.put({"score":top_scores,
                                   "pos":top_pos,
                                   "neg":top_neg,
                                   "pattern":top_pattern})
            #self._pattern_queue.put(top_pattern)

    def _bin_array(self, num, m):
        """Convert a positive integer num into an m-bit bit vector
        """
        return array(list(binary_repr(num).zfill(m))).astype(int8)