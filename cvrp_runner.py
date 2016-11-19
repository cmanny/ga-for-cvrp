from cvrp_info import CVRPInfo
from cvrp_simplega import CVRPSimpleGA
import os
import threading
import copy
import multiprocessing
from multiprocessing.managers import BaseManager

class MyManager(BaseManager): pass

def Manager():
    m = MyManager()
    m.start()
    return m

MyManager.register('CVRPSimpleGA', CVRPSimpleGA)

def run_thread(which, i_step):
    which.step(i_step)

class CVRPRunner(object):

    def __init__(self, algorithm,  iterations):
        self.manager = Manager()
        self.algorithm = algorithm
        self.algorithms = [None for _ in range(4)]
        for i in range(4):
            self.algorithms[i] = self.manager.CVRPSimpleGA(CVRPInfo("fruitybun250.vrp", debug=True))
            self.algorithms[i].randomize(1000)
        self.threads = [None for i in range(4)]
        self.best_solutions = [0,0,0,0]
        self.print_cycle = 1
        self.num_iter = iterations
        self.iter_step = 2

    def run(self):
        for i in range(0, self.num_iter, self.iter_step):
            print("Iteration: " + str(i))
            pool = multiprocessing.Pool(multiprocessing.cpu_count())
            for i in range(4):
                pool.apply(func=run_thread, args=(self.algorithms[i],self.iter_step))
            pool.close()
            pool.join()
            for j in range(4):
                self.best_solutions[j] = self.algorithms[j].get_best()
                print("Thread " + str(j) + " : " + str(self.best_solutions[j].cost))

        for i in range(4):
            print("Thread " + str(i) + " : " + str(self.best_solutions[i]) + '\n')
        print("Best solution: " + str(min(self.best_solutions, lambda x: x.cost)))
        print("Cost: " + str(min([x.cost for x in self.best_solutions])))

    def write_to_file(self, file_name):
        text = os.linesep.join(["login cm13558 65195",
                "name Callum Mann",
                "algorithm Simple GA",
                "cost " + str(self.algorithm.best_solution.cost),
                str(self.algorithm.best_solution)])
        with open(file_name, "w") as f:
            f.write(text)



if __name__ == "__main__":
    cvrp = CVRPRunner(CVRPSimpleGA(CVRPInfo("fruitybun250.vrp", debug=True)), 100)
    cvrp.run()
    cvrp.write_to_file("best-solution.txt")
