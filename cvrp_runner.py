from cvrp_info import CVRPInfo
from cvrp_simplega import CVRPSimpleGA

class CVRPRunner(object):

    def __init__(self, algorithm, data_file, iterations):
        self.algorithm = algorithm
        self.algorithm.info(CVRPInfo(data_file))
        self.algorithm.init()
        self.print_cycle = 1

    def run(self):
        for i in range(iterations):
            cost = self.algorithm.step()
            if i % self.print_cycle == 0:
                print cost



if __name__ == "__main__":
    cvrp = CVRPRunner(CVRPSimpleGA(), "fruitybun250.vrp", 5000)
    cvrp.run()
