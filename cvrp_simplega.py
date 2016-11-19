from cvrp_algorithm import CVRPAlgorithm
import random
import copy
import threading

from heapq import *

class CVRPPopulation(object):
    def __init__(self, info):
        self.info = info
        self.mutate_prob = 0.003
        self.chromosomes = [self.info.make_random_solution() for _ in range(2000)]
        self.best_solution = self.chromosomes[0]
        self.chromo_q = []
        self.zeroDelta = 0
        self.last_best = None
        self.iters = 0
        self.change_diffs = []
        self.injected_chroms = []
        random.seed()

    def step(self):
        self.iters += 1
        self.chromo_q = []
        for x in self.chromosomes:
            heappush(self.chromo_q, (x.cost, x))
        best = self.chromo_q[0][1]
        self.pmx()
        if best.cost < self.best_solution.cost:
            self.last_best = self.best_solution
            self.best_solution = best
            self.change_diffs.append(self.best_solution.cost - self.last_best.cost)
        else:
            self.zeroDelta += 1
        return (self.best_solution, self.change_diffs[-1] / sum(self.change_diffs))

    def pmx(self):
        best = [heappop(self.chromo_q)[1] for _ in range(4)] + self.injected_chroms
        if self.zeroDelta == 4:
             for i in range(4):
                 best += [self.info.make_random_solution()]
            #best = [self.info.optimise_path_order(x) for x in best]
             self.zeroDelta = 0
        self.chromosomes = [best[0]]
        random.seed()
        for i in range(len(best)):
            for j in range(i, len(best)):
                start = random.randrange(0, 248)
                end = random.randrange(0, 248)
                while start == end:
                    end = random.randrange(0, 248)
                if start > end:
                    start, end = end, start
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


class CVRPSimpleGA(CVRPAlgorithm):
    def __init__(self, info, num_populations):
        super(CVRPSimpleGA, self).__init__(info)

        self.populations = [CVRPPopulation(self.info) for _ in range(num_populations)]
        self.pop_bests = [0 for _ in range(num_populations)]
    def step(self):
        if self.populations[0].iters % 10 == 0:
            for p in self.populations:
                c = p.chromosomes[0]
                #print(",".join([str(x) for x in c.chromosome.string]))
        for i, pop in enumerate(self.populations):
            self.pop_bests[i], ratio = pop.step()
        return min(self.pop_bests, key = lambda x: x.cost)

    def inject_population(self, pop_to_inject, chroms):
        pop_to_inject.injected_chroms = chroms


if __name__ == "__main__":
    print("Run cvrp_runner instead")
