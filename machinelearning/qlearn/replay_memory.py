import numpy as np

import random

import torch
from torch.autograd import Variable

# The implementation of the replay memory

class ReplayMemory(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
    
    def push(self, event):
        self.memory.append(event)

        if len(self.memory) > self.capacity:
            del self.memory[0]
    
    def sample(self, batch_size):
        samples = zip(*random.sample(self.memory, batch_size))
        return map(lambda x: Variable(torch.cat(x, 0)), samples)

# # DEBUGGING
# memory = ReplayMemory(10)
# for i in range(0, 10):
#     param1 = torch.Tensor([i])
#     param2 = torch.Tensor([i])
#     param3 = torch.LongTensor([i])
#     memory.push((param1, param2, param3)) # events will have a different format in practice

# samples = memory.sample(10)
# for sample in samples:
#     print("%s" % sample)

# # we get same numbers at the same indexes in different returned samples -> shows they are concatenated along a dimension