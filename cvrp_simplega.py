from cvrp_algorithm import CVRPAlgorithm
import random
import copy

from heapq import *

class CVRPSimpleGA(CVRPAlgorithm):
    def __init__(self, info):
        super(CVRPSimpleGA, self).__init__(info)

        #chromosomes are solutions
        self.mutate_prob = 0.001
        self.chromosomes = [self.info.make_random_solution() for _ in range(2000)]
        self.best_solution = self.chromosomes[0]
        self.chromo_q = []
        random.seed()


    def step(self):
        self.chromo_q = []
        for x in self.chromosomes:
            heappush(self.chromo_q, (x.cost, x))
        best = self.chromo_q[0][1]
        self.pmx()
        if best.cost < self.best_solution.cost:
            self.best_solution = best
        #raw_input()
        return self.best_solution.cost

    def pmx(self):
        best = [heappop(self.chromo_q)[1] for _ in range(10)]
        self.chromosomes = []
        random.seed()
        for i in range(len(best)):
            for j in range(len(best)):
                start = random.randrange(0, 248)
                end = random.randrange(0, 248)
                if start > end:
                    tmp = end
                    end = start
                    start = tmp
                if start == end:
                    start = 0
                    end = 248
                mum, dad = best[i], best[j]
                baby1_chrom = copy.deepcopy(mum.chromosome)
                baby2_chrom = copy.deepcopy(dad.chromosome)
                for k in range(start, end):
                    mum_g, dad_g = mum.chromosome.string[k], dad.chromosome.string[k]
                    baby1_chrom.swap(mum_g, dad_g)
                    baby2_chrom.swap(mum_g, dad_g)
                self.mutate(baby1_chrom)
                self.mutate(baby2_chrom)
                baby1 = self.info.make_from_string(baby1_chrom.string)
                baby2 = self.info.make_from_string(baby2_chrom.string)
                self.chromosomes += [baby1, baby2]
        #print("-".join([str(x.cost) for x in self.chromosomes]))

    def mutate(self, chromosome):
        for i in range(len(chromosome.string)):
            if random.uniform(0, 1) <= self.mutate_prob:
                rint = random.randrange(0, 248)
                chromosome.swap(chromosome.string[i], chromosome.string[rint])


if __name__ == "__main__":
    print("Run cvrp_runner instead")
