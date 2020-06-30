from collections import defaultdict

import numpy as np

from .dist import all_gather, is_dist_avail_and_initialized


class LogBuffer(object):
    def __init__(self):
        self.value_history = defaultdict(list)
        self.n_history = defaultdict(list)

    def clear(self):
        self.value_history.clear()
        self.n_history.clear()

    def update(self, values, count=1):
        assert isinstance(values, dict)
        for key, value in values.items():
            self.value_history[key].append(value)
            self.n_history[key].append(count)

    def average(self, n=0):
        """Average latest n values or all values"""
        assert n >= 0
        outputs = {}
        for key in self.value_history:
            values = np.array(self.value_history[key][-n:])
            nums = np.array(self.n_history[key][-n:])
            avg = np.sum(values * nums) / np.sum(nums)
            outputs[key] = avg
        return outputs

    def synchronize_between_processes(self):
        if is_dist_avail_and_initialized():
            value_history_list = all_gather(self.value_history)
            n_history_list = all_gather(self.n_history)
            self.clear()
            for i, (value_history, n_history) in enumerate(zip(value_history_list, n_history_list)):
                for key in n_history:
                    self.value_history[key].extend(value_history[key])
                    self.n_history[key].extend(n_history[key])
        return self.average()
