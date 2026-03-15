import os

class Solution: 
    def __init__(self, status, obj_value, dualBound, runtime):
        self.obj_value = obj_value
        self.runtime = runtime
        self.status = status
        self.dualBound = dualBound

    def value(self):
        return self.obj_value

def recordSolution(data, solution, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir) 
        # TODO