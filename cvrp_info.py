import os
import math
import random

class Path(object):
    def __init__(self, path=[], cost=0, is_valid=False, demand=0):
        self.is_valid = is_valid
        self.path = path
        self.cost = cost
        self.demand = demand

    def __repr__(self):
        return "->".join(str(n) for n in self.path)

class Solution(object):
    def __init__(self, paths=[], cost=0, is_valid=False, demand=0):
        self.is_valid = is_valid
        self.paths = paths
        self.cost = cost
        self.demand = demand

    def __repr__(self):
        return "\n".join([str(path) for path in self.paths])

class CVRPInfo(object):

    def __init__(self, data_file):
        self.read_data(data_file)
        self.compute_dists()
        self.start_node = 1
        random.seed()

    #the vrp file is such an awful format
    def read_data(self, data_file):
        with open(data_file) as f:
            content = [line.rstrip("\n") for line in f.readlines()]
        self.dimension = int(content[0].split()[-1])
        self.capacity = int(content[0].split()[-1])

        self.demand = [-1 for _ in range(self.dimension + 1)]
        self.coords = [(-1, -1) for _ in range(self.dimension + 1)]

        for i in range(3, self.dimension + 3):
            nid, xc, yc = [int(x) for x in content[i].split()]
            self.coords[nid] = (xc, yc)
        for i in range(self.dimension + 4, 2 * (self.dimension + 2)):
            nid, dem = [int(x) for x in content[i].split()]
            self.demand[nid] = dem

    def compute_dist(self, n1, n2):
        n1 = self.coords[n1]
        n2 = self.coords[n2]
        return math.sqrt((n1[0] - n2[0])**2 + (n1[1] - n2[1])**2)

    def compute_dists(self):
        self.dist = [list([-1 for _ in range(self.dimension + 1)]) \
                        for _ in range(self.dimension + 1)]
        for xi in range(self.dimension):
            for yi in range(self.dimension):
                self.dist[xi][yi] = self.compute_dist(xi, yi)

    def make_solution(self, paths):
        cost = 0
        demand = 0
        is_valid = True
        visited = set()
        for path in paths:
            if not path.is_valid:
                is_valid = False
            cost += path.cost
            demand += path.demand
        sol = Solution(cost=cost, demand=demand, is_valid=is_valid, paths=paths)
        return sol


    def make_path(self, node_list):
        if node_list[0] != self.start_node:
            return None
        cost = 0
        demand = 0
        is_valid = True
        for i in range(1, len(node_list)):
            n1, n2 = node_list[i - 1], node_list[i]
            cost += self.dist[n1][n2]
            demand += self.demand[n2]
        if demand > self.capacity:
            is_valid = False

        path = Path(cost=cost, demand=demand, is_valid=is_valid, path=node_list)
        return path

    def make_random_solution(self):
        unserviced = [i for i in range(2, self.dimension + 1)]
        paths = []
        cur_path = [1]
        path_demand = 0
        while unserviced:
            rint = random.randrange(len(unserviced))
            node = unserviced[rint]
            if path_demand + self.demand[node] <= self.capacity:
                cur_path += [node]
                path_demand += self.demand[node]
                del unserviced[rint]
                continue
            cur_path += [1]
            paths += [self.make_path(cur_path)]
            cur_path = [1]
            path_demand = 0
        return self.make_solution(paths)






    def __repr__(self):
        strin = {
            "coords" : self.coords,
            "demand" : self.demand,
            #"dists"  : self.dist
        }
        return str(strin)

if __name__ == "__main__":
    ci = CVRPInfo("fruitybun250.vrp")
    sol = ci.make_random_solution()
    print(sol)
    print("cost: " + str(sol.cost))
