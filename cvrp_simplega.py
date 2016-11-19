from cvrp_algorithm import CVRPAlgorithm

from heapq import *

class CVRPSimpleGA(CVRPAlgorithm):
    def __init__(self, info):
        super(CVRPSimpleGA, self).__init__(info)

        #chromosomes are solutions
        self.chromosomes = [self.info.make_random_solution() for _ in range(2000)]
        self.best_solution = self.chromosomes[0]
        self.chromo_q = []
        for x in self.chromosomes:
            heappush(self.chromo_q, (x.cost, x))



    def step(self):
        new_rand = self.info.make_random_solution()
        heappush(self.chromo_q, (new_rand.cost, new_rand))
        best = heappop(self.chromo_q)[1]
        if best.cost < self.best_solution.cost:
            self.best_solution = best
        return best.cost

if __name__ == "__main__":
    print("Run cvrp_runner instead")
