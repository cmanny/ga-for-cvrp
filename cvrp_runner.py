from cvrp_info import CVRPInfo
from cvrp_simplega import CVRPSimpleGA
import os

class CVRPRunner(object):

    def __init__(self, algorithm,  iterations):
        self.algorithm = algorithm
        self.print_cycle = 1
        self.num_iter = iterations

    def run(self):
        for i in range(self.num_iter):
            cost = self.algorithm.step()
            if i % self.print_cycle == 0:
                print cost
        print("Best solution: " + str(self.algorithm.best_solution))
        print("Cost: " + str(self.algorithm.best_solution.cost))

    def write_to_file(self, file_name):
        text = os.linesep.join(["login cm13558 65195",
                "name Callum Mann",
                "algorithm Simple GA",
                "cost " + str(self.algorithm.best_solution.cost),
                str(self.algorithm.best_solution)])
        with open(file_name, "w") as f:
            f.write(text)



if __name__ == "__main__":
    cvrp = CVRPRunner(CVRPSimpleGA(CVRPInfo("fruitybun250.vrp", debug=True)), 10000)
    cvrp.run()
    cvrp.write_to_file("best-solution.txt")
