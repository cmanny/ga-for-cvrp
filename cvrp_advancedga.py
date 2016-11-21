from cvrp_algorithm import CVRPAlgorithm
import random
import copy
import threading
import collections

from heapq import *

class AGAPopulation(object):
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
            self.zeroDelta = 0
        else:
            self.zeroDelta += 1
        return (self.best_solution, self.change_diffs[-1] / sum(self.change_diffs))

    def pmx(self):
        best = [heappop(self.chromo_q)[1] for _ in range(5)] + self.injected_chroms
        # if self.zeroDelta and self.zeroDelta % 10 == 0:
        #     add = 0
        #     if self.zeroDelta % 50 == 0:
        #         add = 8
        #         self.zeroDelta = 0
        #     if self.zeroDelta % 100 == 0:
        #         add = 14
        #     for i in range(2 + add):
        #         best += [self.info.make_random_solution()]

            #best = [self.info.optimise_path_order(x) for x in best]
        self.chromosomes = [best[0]]
        random.seed()
        for i in range(len(best)):
            for j in range(i, len(best)):
                mum, dad = best[i], best[j]
                baby1_chrom = copy.deepcopy(mum.chromosome)
                baby2_chrom = copy.deepcopy(dad.chromosome)
                if random.uniform(0,1) < 0.75:
                    start, end = self.rand_points(0, self.info.dimension - 2)
                    for k in range(start, end):
                        mum_g, dad_g = mum.chromosome.string[k], dad.chromosome.string[k]
                        baby1_chrom.swap(mum_g, dad_g)
                        baby2_chrom.swap(mum_g, dad_g)
                else:
                    self.swap_node(baby1_chrom)
                    self.swap_node(baby2_chrom)
                if random.uniform(0, 1) < self.mutate_prob:
                    self.mutate(baby1_chrom)
                    self.mutate(baby2_chrom)
                baby1 = self.info.make_from_string(baby1_chrom.string)
                baby2 = self.info.make_from_string(baby2_chrom.string)
                self.chromosomes += [baby1, baby2]

    def rand_points(self, low, high):
        start = random.randrange(low, high)
        end = random.randrange(low, high)
        while start == end:
            end = random.randrange(low, high)
        if start > end:
            start, end = end, start
        return start, end

    def swap_many_nodes(self, chromosome):
        for i in range(len(chromosome.string)):
            if random.uniform(0, 1) <= self.mutate_prob:
                self.swap_node(chromosome)

    def swap_node(self, chromosome):
        rint = random.randrange(0, self.info.dimension - 2)
        rint2 = random.randrange(0, self.info.dimension - 2)
        chromosome.swap(chromosome.string[rint2], chromosome.string[rint])

    #mutations
    def inversion(self, chromosome):
        start, end = self.rand_points(0, self.info.dimension - 2)
        cs = chromosome.string
        new_string = cs[0:start] + cs[start:end][::-1] + cs[end:self.info.dimension - 1]
        if len(new_string) != len(cs):
            print(start)
            print(end)
            print(len(new_string))
            print(len(cs))
            print(cs)
            print(new_string)
            print([x - y for x, y in zip(cs, new_string)])
            #raw_input()
        chromosome.string = new_string

    def swap_sequence(self, chromosome):
        fs, fe = self.rand_points(0, self.info.dimension - 10)
        ss, se = self.rand_points(fe + 1, self.info.dimension - 5)
        cs = chromosome.string
        new_str = cs[0:fs] + cs[ss:se] + cs[fe:ss] + cs[fs:fe]
        new_str += cs[len(new_str):self.info.dimension - 1]
        if len(cs) != len(new_str):
            print [item for item, count in collections.Counter(new_str).items() if count > 1]
            print(fs)
            print(fe)
            print(ss)
            print(se)
            print(len(new_str))
            print(len(cs))
            print(cs)
            print(new_str)
        chromosome.string = new_str


    def mutate(self, chromosome):
        if random.uniform(0, 1) < 0.9999:
            self.inversion(chromosome)
        else:
            self.swap_sequence(chromosome)

class CVRPAdvancedGA(CVRPAlgorithm):
    def __init__(self, info, num_populations):
        super(CVRPAdvancedGA, self).__init__(info)

        self.populations = [AGAPopulation(self.info) for _ in range(num_populations)]
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
