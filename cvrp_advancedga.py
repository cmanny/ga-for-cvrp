from cvrp_algorithm import CVRPAlgorithm
import random
import copy
import threading

from heapq import *

class AGAPopulation(object):
    def __init__(self, info, total_iters):
        self.info = info
        self.info.max_route_len = 10
        self.mutate_prob = 0.01
        self.chromosomes = []
        for x in [self.info.steep_improve_solution(self.info.make_random_solution(greedy=True)) for _ in range(100)]:
            heappush(self.chromosomes, (x.cost, x))
        self.best_solution = self.chromosomes[0][1]
        self.zeroDelta = 0
        self.iters = 0
        self.total_iters = total_iters
        self.change_diffs = []
        self.injected_chroms = []
        self.pop = 5
        self.same_route_prob = 0.25
        random.seed()

    def step(self):
        p1, p2 = self.tournament_selection(self.chromosomes)
        child = self.simple_random_crossover(p1, p2)
        self.info.refresh(child)
        self.simple_random_mutation(child)
        if self.chromosomes[0][1].cost < self.best_solution.cost:
            self.best_solution = self.chromosomes[0][1]
        self.chromosomes.remove(nlargest(1, self.chromosomes)[0])
        self.info.refresh(child)
        self.repairing(child)
        self.info.refresh(child)
        self.info.steep_improve_solution(child)
        self.info.refresh(child)

        heapify(self.chromosomes)
        heappush(self.chromosomes, (self.fitness(child), child))
        self.iters += 1
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
        mnv = sum(self.info.demand[i] for i in range(250)) / self.info.capacity
        alpha = self.best_solution.cost / ((1 / (self.iters + 1)) * (self.info.capacity * mnv / 2)**2 + 0.00001)
        penalty = alpha * penalty_sum * self.iters / self.total_iters
        chromosome.penalty = penalty
        return penalty

    # returns true when a repair was needed, false otherwise
    def repairing(self, chromosome):
        routes = chromosome.routes
        r_max_i = max((i for i in range(len(routes))), key = lambda i: routes[i].demand)
        r_min_i = min((i for i in range(len(routes))), key = lambda i: routes[i].demand)
        if routes[r_max_i].demand > self.info.capacity:
            rint = random.randrange(1, len(routes[r_max_i].route) - 1)
            routes[r_min_i].append_node(routes[r_max_i].route[rint])
            routes[r_max_i].remove_node(routes[r_max_i].route[rint])
            return True
        return False

    def tournament_selection(self, chromosomes):
        return chromosomes[random.randrange(0, 10)][1], chromosomes[random.randrange(0, len(chromosomes) - 1)][1]

    def simple_random_crossover(self, chrom1, chrom2):
        child = copy.deepcopy(chrom1)
        sub_route = chrom2.random_subroute()
        for x in sub_route:
            child.remove_node(x)
        r_id, n_id = self.best_insertion(child, sub_route)
        #print("{} {}".format(r_id, n_id))
        child.insert_route(r_id, n_id, sub_route)
        return child

    def simple_random_mutation(self, chromosome):
        r_i = random.randrange(0, len(chromosome.routes))
        while(len(chromosome.routes[r_i].route) == 2):
            r_i = random.randrange(0, len(chromosome.routes))
        c_i = random.randrange(1, len(chromosome.routes[r_i].route) - 1)
        node = chromosome.routes[r_i].route[c_i]
        chromosome.remove_node(node)
        if random.uniform(0, 1) < self.same_route_prob:
            _, best = self.best_route_insertion([node], chromosome.routes[r_i].route)
            best_i = (r_i, best)
        else:
            r_r_i = r_i
            while r_i == r_r_i:
                r_r_i = random.randrange(0, len(chromosome.routes))
            _, best = self.best_route_insertion([node], chromosome.routes[r_r_i].route)
            best_i = (r_r_i, best)
        chromosome.insert_route(best_i[0], best_i[1], [node])

    #finds the index where the route is best inserted
    def best_route_insertion(self, sub_route, route):
        start = sub_route[0]
        end = sub_route[-1]
        best_payoff, best_i = 0, 0
        dist = self.info.dist
        i = 0
        for i in range(0, len(route) - 1):
            init_cost = dist[route[i]][route[i + 1]]
            payoff = init_cost - dist[route[i]][start] - dist[end][route[i + 1]]
            if payoff > best_payoff:
                best_payoff, best_i = payoff, i
        return best_payoff, i

    #finds the best route index, and node index where the route should go
    def best_insertion(self, child, sub_route):
        best_payoff, best_rid, best_nid = -1, 0, 0
        for r_id, route in enumerate(child.routes):
            route = route.route
            subopt_best, n_id = self.best_route_insertion(sub_route, route)
            if subopt_best > best_payoff:
                best_payoff, best_rid, best_nid = subopt_best, r_id, n_id
        #print(best_payoff)
        return best_rid, best_nid


class CVRPAdvancedGA(CVRPAlgorithm):
    def __init__(self, info, num_populations, total_iters):
        super(CVRPAdvancedGA, self).__init__(info)

        self.populations = [AGAPopulation(self.info, total_iters) for _ in range(num_populations)]
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
