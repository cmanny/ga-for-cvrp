from cvrp_info import CVRPInfo
from cvrp_simplega import CVRPSimpleGA

class CVRPRunner(object):

    def __init__(self, algorithm, data_file):
        self.algorithm = algorithm
        self.algorithm.info(CVRPInfo(data_file))

    def run(self):
        self.algorithm.run()


if __name__ == "__main__":
    cvrp = CVRPRunner(CVRPSimpleGA(5000), "fruitybun250.vrp")
    cvrp.run()
