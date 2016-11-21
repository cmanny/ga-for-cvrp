from cvrp_algorithm import CVRPAlgorithm
import random
import copy
import threading

from heapq import *

class SGAPopulation(object):
    def __init__(self, info):
        self.info = info
        self.mutate_prob = 0.009
        self.chromosomes = [self.info.make_random_solution() for _ in range(2000)]
        self.best_solution = self.chromosomes[0]
        self.chromo_q = []
        self.zeroDelta = 0
        self.last_best = None
        self.iters = 0
        self.change_diffs = []
        self.injected_chroms = []
        self.pop = 10
        random.seed()

    def step(self):
        self.iters += 1
        self.chromo_q = []
        hashes = set()
        for x in self.chromosomes:
            chromo = x
            if chromo.chromosome.hash in hashes:
                chromo = self.info.make_random_solution()
            else:
                hashes.add(chromo.chromosome.hash)
            heappush(self.chromo_q, (chromo.cost, chromo))
        best = self.chromo_q[0][1]
        self.pmx()
        if best.cost < self.best_solution.cost:
            self.last_best = self.best_solution
            self.best_solution = best
            self.change_diffs.append(self.best_solution.cost - self.last_best.cost)
            self.zeroDelta = 0
        else:
            self.zeroDelta += 1
        return (self.best_solution, self.change_diffs[-1] / sum(self.change_diffs))

    def pmx(self):
        best = [self.info.steep_improve_solution(heappop(self.chromo_q)[1]) for _ in range(self.pop)] + self.injected_chroms
            #best = [self.info.optimise_path_order(x) for x in best]
        self.chromosomes = [best[0]]
        random.seed()
        for i in range(len(best)):
            for j in range(i + 1, len(best)):
                start = random.randrange(0, self.info.dimension - 2)
                end = random.randrange(0, self.info.dimension - 2)
                while start == end:
                    end = random.randrange(0, self.info.dimension - 2)
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
                self.swap_node(chromosome, i, random.randrange(0, self.info.dimension - 2))
    def swap_node(self, chromosome, i, j):
        chromosome.swap(chromosome.string[i], chromosome.string[j])


class CVRPSimpleGA(CVRPAlgorithm):
    def __init__(self, info, num_populations):
        super(CVRPSimpleGA, self).__init__(info)

        self.populations = [SGAPopulation(self.info) for _ in range(num_populations)]
        self.pop_bests = [0 for _ in range(num_populations)]
    def step(self):
        if self.populations[0].iters % 10 == 0:
            for p in self.populations:
                c = p.chromosomes[0]
                #print(",".join([str(x) for x in c.chromosome.string]))
        for i, pop in enumerate(self.populations):
            self.pop_bests[i], ratio = pop.step()
        self.best_solution = min(self.pop_bests, key = lambda x: x.cost)
        return self.best_solution

    def inject_population(self, pop_to_inject, chroms):
        pop_to_inject.injected_chroms = chroms


if __name__ == "__main__":
    print("Run cvrp_runner instead")
