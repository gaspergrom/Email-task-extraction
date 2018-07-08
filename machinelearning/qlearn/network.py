import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.autograd import Variable

# The implementation of the neural network

class Network(nn.Module):

    def __init__(self, layer_sizes):
        super(Network, self).__init__()
        self.connections = []
        
        for i in range(0, len(layer_sizes) - 1):
            self.add_layer(layer_sizes[i], layer_sizes[i + 1])
    
    # TODO: different activator functions for different layers/connections (instead of only rectifier)?
    def forward(self, input):
        val = None

        for i in range(0, len(self.connections) - 1):
            if val is None:
                next_input = input
            else:
                next_input = val
            val = F.relu(self.connections[i](next_input))
        
        q_values = self.connections[-1](val)
        return q_values

    # TODO: different types of connections for different layers?
    def add_layer(self, input_size, output_size):
        self.connections.append(nn.Linear(input_size, output_size))
    
    def to_string(self):
        string = "Network - total %d connections:" % len(self.connections)
        
        for i in range(0, len(self.connections)):
            string += "\n%s" % self.connections[i]

        string += "\n------------------\nNetwork input size: %d\nNetwork output size: %d" % (self.connections[0].in_features, self.connections[-1].out_features)
        return string

## DEBUGGING ##
# test = Network([10, 20, 30, 40])
# print(test.to_string())
# print(test.forward(Variable(torch.Tensor(10))))