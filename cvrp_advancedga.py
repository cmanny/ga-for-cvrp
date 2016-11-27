from cvrp_algorithm import CVRPAlgorithm
import random
import copy
import threading

from heapq import *

class AGAPopulation(object):
    def __init__(self, info):
        self.info = info
        self.info.max_route_len = 10
        self.mutate_prob = 0.003
        self.chromosomes = []
        for x in [self.info.steep_improve_solution(self.info.make_random_solution()) for _ in range(200)]:
            heappush(self.chromosomes, (x.cost, x))
        self.best_solution = self.chromosomes[0][1]
        self.zeroDelta = 0
        self.iters = 0
        self.change_diffs = []
        self.injected_chroms = []
        self.pop = 5
        self.same_route_prob = 0.25

        self.alpha = 5
        random.seed()

    def step(self):
        p1, p2 = self.tournament_selection(self.chromosomes)
        child = self.simple_random_crossover(p1, p2)
        self.simple_random_mutation(child)
        if child.cost < self.best_solution.cost:
            self.best_solution = child
        self.chromosomes.remove(nlargest(1, self.chromosomes)[0])
        self.repairing(child)
        heapify(self.chromosomes)
        heappush(self.chromosomes, (self.fitness(child), child))
        return self.best_solution

    #calc fitness
    def fitness(self, chromosome):
        penalty = self.penalty(chromosome)
        return chromosome.cost + penalty

    #calculates our penalty
    def penalty(self, chromosome):
        penalty_sum = 0
        for route in chromosome.routes:
            penalty_sum += max(0, route.demand - self.info.capacity)**2
        penalty = self.alpha * penalty_sum
        chromosome.penalty = penalty
        return penalty

    # returns true when a repair was needed, false otherwise
    def repairing(self, chromosome):
        routes = chromosome.routes
        r_max_i = max((i for i in range(len(routes))), key = lambda i: routes[i].demand)
        r_min_i = min((i for i in range(len(routes))), key = lambda i: routes[i].demand)
        if routes[r_max_i].demand > self.info.capacity:
            rint = random.randrange(0, len(routes[r_max_i]))
            routes[r_min_i].append_node(routes[r_max_i][rint])
            routes[r_max_i].remove_node(routes[r_max_i][rint])
            return True
        return False

    def tournament_selection(self, chromosomes):
        return chromosomes[0][1], chromosomes[1][1]

    def simple_random_crossover(self, chrom1, chrom2):
        child = copy.deepcopy(chrom1)
        sub_route = chrom2.random_subroute()
        for x in sub_route:
            child.remove_node(x)
        r_id, n_id = self.best_insertion(child, sub_route)
        child.insert_route(r_id, n_id, sub_route)
        return child

    def simple_random_mutation(self, chromosome):
        r_i = random.randrange(0, len(chromosome.routes))
        c_i = random.randrange(1, len(chromosome.routes[r_i].route) - 1)
        node = chromosome.routes[r_i].route[c_i]
        chromosome.remove_node(node)
        if random.uniform(0, 1) < self.same_route_prob:
            best_i = (r_i, self.best_route_insertion([node], chromosome.routes[r_i].route))
        else:
            r_r_i = r_i
            while r_i == r_r_i:
                r_r_i = random.randrange(0, len(chromosome.routes))
            best_i = (r_r_i, self.best_route_insertion([node], chromosome.routes[r_r_i].route))
        chromosome.insert_route(best_i[0], best_i[1], [node])

    #finds the index where the route is best inserted
    def best_route_insertion(self, sub_route, route):
        start = sub_route[0]
        end = sub_route[-1]
        for i in range(0, len(route) - 1):
            pass
        return 0

    #finds the best route index, and node index where the route should go
    def best_insertion(self, child, sub_route):
        return 0, 0

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
        chromosome.string = new_string

    def swap_sequence(self, chromosome):
        fs, fe = self.rand_points(0, self.info.dimension - 10)
        ss, se = self.rand_points(fe + 1, self.info.dimension - 5)
        cs = chromosome.string
        new_str = cs[0:fs] + cs[ss:se] + cs[fe:ss] + cs[fs:fe]
        new_str += cs[len(new_str):self.info.dimension - 1]
        chromosome.string = new_str


    def mutate(self, chromosome):
        if random.uniform(0, 1) < 0.5:
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
            self.pop_bests[i] = pop.step()
        self.best_solution = min(self.pop_bests, key = lambda x: x.cost)
        return self.best_solution

    def inject_population(self, pop_to_inject, chroms):
        pop_to_inject.injected_chroms = chroms


if __name__ == "__main__":
    print("Run cvrp_runner instead")
