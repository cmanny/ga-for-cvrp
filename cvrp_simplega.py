from cvrp_algorithm import CVRPAlgorithm
import random

from heapq import *

class CVRPSimpleGA(CVRPAlgorithm):
    def __init__(self, info):
        super(CVRPSimpleGA, self).__init__(info)

        #chromosomes are solutions
        self.chromosomes = [self.info.make_random_solution() for _ in range(2000)]
        self.best_solution = self.chromosomes[0]
        self.chromo_q = []
        random.seed()


    def step(self):
        self.chromo_q = []
        for x in self.chromosomes:
            heappush(self.chromo_q, (x.cost, x))
        best = self.chromo_q[0][1]
        #self.pmx()
        if best.cost < self.best_solution.cost:
            self.best_solution = best
        return self.best_solution.cost

    def pmx(self):
        best = [heappop(self.chromo_q)[1] for _ in range(10)]
        self.chromosomes = []
        for i in range(len(best)):
            for j in range(len(best)):
                rint = random.randrange(0, 247)
                mum, dad = best[i], best[j]
                print(mum.chromosome.index_map)
                print(dad.chromosome.index_map)
                mum_g, dad_g = mum.chromosome.string[rint], dad.chromosome.string[rint]
                baby1 = mum.chromosome.swap(mum_g, dad_g)
                baby2 = dad.chromosome.swap(mum_g, dad_g)
                baby1, baby2 = self.info.make_from_string(baby1), self.info.make_from_string(baby2)
                self.chromosomes += [baby1, baby2]



if __name__ == "__main__":
    print("Run cvrp_runner instead")
