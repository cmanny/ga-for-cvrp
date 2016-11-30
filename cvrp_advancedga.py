from cvrp_algorithm import CVRPAlgorithm
import random
import copy
import threading

from heapq import *

class AGAPopulation(object):
    def __init__(self, info, total_iters):
        self.info = info
        self.info.max_route_len = 10
        self.chromosomes = []
        for x in [self.info.steep_improve_solution(self.info.make_random_solution(greedy=True)) for _ in range(800)]:
            heappush(self.chromosomes, (x.cost, x))
        self.best_solution = self.chromosomes[0][1]
        self.iters = 0
        self.total_iters = total_iters
        self.same_route_prob = 0.25
        random.seed()

    def step(self):
        replace = 1
        for i in range(12):
            for j in range(i + 1, 12):
                ic, jc = self.chromosomes[i][1], self.chromosomes[j][1]
                if random.uniform(0, 1) < 0.2:
                    jc = self.chromosomes[random.randrange(10, len(self.chromosomes) - 1)][1]
                child = self.biggest_overlap_crossover(ic, jc)
                if random.uniform(0, 1) < 0.95:
                    for _ in range(3):
                        c = self.biggest_overlap_crossover(ic, child)
                        self.info.refresh(c)
                        if c.cost < child.cost:
                            child = c
                else:
                    for _ in range(3):
                        c = self.simple_random_crossover(ic, child)
                        self.info.refresh(c)
                        if c.cost < child.cost:
                            child = c
                self.info.refresh(child)
                self.simple_random_mutation(child)
                self.info.refresh(child)
                self.repairing(child)
                self.info.refresh(child)
                self.info.steep_improve_solution(child)
                self.info.refresh(child)
                self.chromosomes[-replace] = (self.fitness(child), child)
                replace += 1
        heapify(self.chromosomes)
        self.iters += 1
        if self.chromosomes[0][1].cost < self.best_solution.cost:
            self.best_solution = self.chromosomes[0][1]
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
        mnv = sum(self.info.demand[i] for i in range(self.info.dimension)) / self.info.capacity
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

    def simple_random_crossover(self, chrom1, chrom2):
        child = copy.deepcopy(chrom1)
        sub_route = chrom2.random_subroute()
        for x in sub_route:
            child.remove_node(x)
        r_id, n_id = self.best_insertion(child, sub_route)
        child.insert_route(r_id, n_id, sub_route)
        return child

    def biggest_overlap_crossover(self, c1, c2):
        child = copy.deepcopy(c1)
        sub_route = c2.random_subroute()
        routes = []
        for x in sub_route:
            child.remove_node(x)
        for i, route in enumerate(child.routes):
            x_min, x_max, y_min, y_max = self.info.bounding_box(route.route)
            sx_min, sx_max, sy_min, sy_max = self.info.bounding_box(sub_route)
            x_overlap = max(0, min(x_max, sx_max) - max(x_min, sx_min))
            y_overlap = max(0, min(y_max, sy_max) - max(y_min, sy_min))
            heappush(routes, (x_overlap * y_overlap, i))
        top3 = nlargest(6, routes)
        min_i = min((i[1] for i in top3), key = lambda x: child.routes[x].demand)
        _, best = self.best_route_insertion(sub_route, child.routes[min_i].route)
        child.insert_route(min_i, best, sub_route)
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
        return best_rid, best_nid


class CVRPAdvancedGA(CVRPAlgorithm):
    def __init__(self, info, num_populations, total_iters):
        super(CVRPAdvancedGA, self).__init__(info)

        self.populations = [AGAPopulation(self.info, total_iters) for _ in range(num_populations)]
        self.pop_bests = [0 for _ in range(num_populations)]
    def step(self):
        for i, pop in enumerate(self.populations):
            self.pop_bests[i] = pop.step()
        self.best_solution = min(self.pop_bests, key = lambda x: x.cost)
        return self.best_solution


if __name__ == "__main__":
    print("Run cvrp_runner instead")
