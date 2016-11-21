from cvrp_info import CVRPInfo
from cvrp_simplega import CVRPSimpleGA
from cvrp_advancedga import CVRPAdvancedGA
import os
import time

class CVRPRunner(object):

    def __init__(self, algorithm,  iterations):
        self.algorithm = algorithm
        self.print_cycle = 10
        self.num_iter = iterations
        self.timings_file = open("timings/timings_{}.txt".format(time.time()), "w")

    def run(self):
        self.start_time = time.time()
        self.im = None
        for i in range(self.num_iter):
            best = self.algorithm.step()
            if i % self.print_cycle == 0:
                self.timings_file.write("{} at {}s\n".format(best.cost, time.time() - self.start_time))
                print best.cost



            # if i % 100:
            #     self.im = self.algorithm.info.visualise(self.algorithm.best_solution)
            #     self.im.save("images/"+str(self.algorithm.best_solution.cost) + ".png")
        print("Best solution: " + str(best))
        print("Cost: " + str(best))


    def write_to_file(self, file_name):
        text = os.linesep.join(["login cm13558 65195",
                "name Callum Mann",
                "algorithm Simple GA",
                "cost " + str(self.algorithm.best_solution.cost),
                str(self.algorithm.best_solution)])
        with open(file_name, "w") as f:
            f.write(text)



if __name__ == "__main__":
    cvrp = CVRPRunner(CVRPAdvancedGA(CVRPInfo("validate/fruitybun250.vrp", debug=True), 1), 500000)
    cvrp.run()
    cvrp.write_to_file("validate/best-solution.txt")
