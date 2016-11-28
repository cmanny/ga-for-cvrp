from cvrp_info import CVRPInfo
from cvrp_advancedga import CVRPAdvancedGA
import os
import time
import signal
import sys

class CVRPRunner(object):

    def __init__(self, algorithm,  iterations):
        self.algorithm = algorithm
        self.print_cycle = 500
        self.num_iter = iterations
        #self.timings_file = open("timings/timings_{0}.txt".format(time.time()), "w")
        self.iter = 0
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):
        handling = True
        while handling:
            print("Iter:{0}\nPath:{1}\nWhat do? E for exec(), V for visualise, C to continue, S to save, X to exit".format(self.iter, self.best))
            c = raw_input()
            if c == "E":
                print("exec:")
                exec(raw_input())
            if c == "S":
                self.write_to_file("best-solution-{0}.part".format(self.iter))
            if c == "C":
                handling = False
            if c == "V":
                self.algorithm.info.visualise(self.best).show()
            elif c == "X":
                exit(0)

    def run(self):
        self.start_time = time.time()
        while self.iter < self.num_iter:
            best = self.algorithm.step()
            self.best = best
            if self.iter % self.print_cycle == 0:
                #self.timings_file.write("{0} at {1}s\n".format(best.cost, time.time() - self.start_time))
                print("iter: {0} best:{1}".format(self.iter, self.best.cost))
            self.iter += 1
            if time.time() - self.start_time > 1800:
                self.write_to_file("best-solution-marking.txt")
                break
            # if i % 100:
            #     self.im = self.algorithm.info.visualise(self.algorithm.best_solution)
            #     self.im.save("images/"+str(self.algorithm.best_solution.cost) + ".png")
        print("Best solution: " + str(best))
        print("Cost: " + str(best.cost))


    def write_to_file(self, file_name):
        text = os.linesep.join(["login cm13558 65195",
                "name Callum Mann",
                "algorithm Advanced GA",
                "cost " + str(self.algorithm.best_solution.cost),
                str(self.algorithm.best_solution)])
        with open(file_name, "w") as f:
            f.write(text)



if __name__ == "__main__":
    cvrp = CVRPRunner(CVRPAdvancedGA(CVRPInfo("fruitybun250.vrp", debug=True), 1, 200000), 200000)
    cvrp.run()
    cvrp.write_to_file("best-solution-marking.txt")
