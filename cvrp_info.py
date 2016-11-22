import os
import math
import random
import threading
from PIL import Image, ImageDraw

class Chromosome(object):
    def __init__(self, string):
        self.index_map = dict()
        for i, x in enumerate(string):
            self.index_map[x] = i
        self.string = string
        self.hash = hash(",".join(str(x) for x in self.string))


    def swap(self, a, b):
        a_index, b_index = self.index_map[a], self.index_map[b]
        self.string[a_index] = b
        self.string[b_index] = a
        self.index_map[a] = b_index
        self.index_map[b] = a_index


class Route(object):
    def __init__(self, route=[], cost=0, is_valid=False, demand=0):
        self.is_valid = is_valid
        self.route = route
        self.cost = cost
        self.demand = demand

    def __repr__(self):
        debug_str = ", cost = " + str(self.cost) + ", demand = " + str(self.demand)
        ret_str = "->".join(str(n) for n in self.route)
        return ret_str + (debug_str if False else "")

class Solution(object):
    bad_count = 0

    def __init__(self, routes=[], cost=0, is_valid=False, demand=0):
        self.is_valid = is_valid
        self.routes = routes
        self.cost = cost
        self.demand = demand
        self.chromise()

    def shuffle(self):
        random.shuffle(self.routes)
        self.chromise()

    def chromise(self):
        string = []
        for p in self.routes:
            string += p.route[1:-1]
        try:
            self.chromosome = Chromosome(string)
        except KeyError:
            print("bad" + str(self))
            Solution.bad_count += 1
            print(Solution.bad_count)
            #print(p.route)

    def __repr__(self):
        return "\n".join([str(route) for route in self.routes])

class CVRPInfo(object):

    def __init__(self, data_file, debug=False):
        self.read_data(data_file)
        self.compute_dists()
        self.start_node = 1
        self.debug = debug
        self.max_route_len = 15
        random.seed()

    #the vrp file is such an awful format
    def read_data(self, data_file):
        with open(data_file) as f:
            content = [line.rstrip("\n") for line in f.readlines()]
        self.dimension = int(content[0].split()[-1])
        self.capacity = int(content[1].split()[-1])

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

    def make_solution(self, routes):
        cost = 0
        demand = 0
        is_valid = True
        visited = set()
        for route in routes:
            if not route.is_valid:
                is_valid = False
            for x in route.route:
                visited.add(x)
            cost += route.cost
            demand += route.demand
        if len(visited) != self.dimension:
            print("NOT ALL VISITED")
            print(visited)
        sol = Solution(cost=cost, demand=demand, is_valid=is_valid, routes=routes)
        #raw_input(junk)
        return sol


    def make_route(self, node_list):
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

        route = Route(cost=cost, demand=demand, is_valid=is_valid, route=node_list)
        return route

    def make_random_solution(self, greedy=False):
        unserviced = [i for i in range(2, self.dimension + 1)]
        #print(unserviced)
        random.shuffle(unserviced)
        routes = []
        cur_route = [1]
        route_demand = 0
        route_length = 0
        while unserviced:
            #print(unserviced)
            i = 0
            if greedy:
                i = min([i for i in range(len(unserviced))], \
                        key=lambda x: self.dist[1][unserviced[i]])
            node = unserviced[i]
            if route_length <= self.max_route_len and route_demand + self.demand[node] <= self.capacity:
                cur_route += [node]
                route_length += 1
                route_demand += self.demand[node]
                #print(cur_route)
                del unserviced[i]
                continue
            cur_route += [1]
            routes += [self.make_route(cur_route)]
            cur_route = [1]
            route_demand = 0
            route_length = 0
        routes += [self.make_route(cur_route + [1])]
        junk = ""
        return self.make_solution(routes)

    def make_from_string(self, chromosome):
        route = [1]
        route_demand = 0
        route_length = 0
        routes = []
        for x in chromosome:
            if route_length <= self.max_route_len and route_demand + self.demand[x] <= self.capacity:
                route += [x]
                route_length += 1
                route_demand += self.demand[x]
                continue
            route += [1]
            routes += [self.make_route(route)]
            route = [1, x]
            route_length = 1
            route_demand = self.demand[x]
        routes += [self.make_route(route + [1])]
        return self.make_solution(routes)

    def optimise_route_order(self, solution):
        routes = []
        for route in solution.routes:
            ordered = sorted([x for x in route.route[1:-1]], key = lambda x: self.dist[1][x])
            routes += [self.make_route([1] + ordered  + [1])]
        return self.make_solution(routes)

    def steep_improve_route(self, route):
        savings = 1
        iters = 0
        while savings > 0:
            savings = 0
            if iters > 1000:
                return route
            for t1_i in range(len(route) - 2):
                for t4_i in range(len(route) - 2):
                    if t4_i != t1_i and t4_i != t1_i + 1 and t4_i + 1 != t1_i:
                        t1 = route[t1_i]
                        t2 = route[t1_i + 1]
                        t3 = route[t4_i + 1]
                        t4 = route[t4_i]
                        diff = self.dist[t1][t2] + self.dist[t4][t3] - self.dist[t2][t3] - self.dist[t1][t4]
                        if diff > savings:
                            savings = diff
                            t1best = t1_i
                            t4best = t4_i
            if savings > 0:
                route[t1best+1], route[t4best] = route[t4best], route[t1best+1]
            iters += 1
        return route

    def steep_improve_solution(self, solution):
        new_routes = []
        for route in solution.routes:
            route = self.steep_improve_route(route.route)
            new_routes += [self.make_route(route)]
        return self.make_solution(new_routes)


    def __repr__(self):
        strin = {
            "coords" : self.coords,
            "demand" : self.demand,
            #"dists"  : self.dist
        }
        return str(strin)

    def write_infos(self):
        distance_str = "distances = {"
        for i in range(len(self.dist)):
            distance_str += str(i) + ": {"
            for j in range(len(self.dist[i])):
                distance_str += str(j) + ":" + str(self.dist[i][j]) + ","
            distance_str += "},"
        distance_str += "}"
        capacity_str = "capacities = {"
        for i, v in enumerate(self.demand):
            capacity_str += str(i) + ":" + str(v) + ","
        capacity_str += "}"
        with open("distances.py", "w") as f:
            f.write(distance_str)
        with open("capacities.py", "w") as f:
            f.write(capacity_str)

    def visualise(self, solution):

        im = Image.new( 'RGB', (500,500), "black") # create a new black image
        draw = ImageDraw.Draw(im)
        color = (0, 0, 0)
        for i, route in enumerate(solution.routes):
            r_c = 255 % (i + 1)
            g_c = 255 % (r_c + 1)
            b_c = 255 % (g_c + 1)
            nodes = route.route
            norm = lambda x, y: (2*x + 250, 2*y + 250)
            draw.line([norm(*self.coords[n]) for n in nodes], fill=(r_c*i, g_c*i, b_c*i), width=2)
        return im











def worker(ci, idd, iters, res):
    best = 1000000000
    best_sol = None
    for i in range(iters):
        sol = ci.make_random_solution(greedy=False)
        if sol.cost < best:
            best = sol.cost
            best_sol = sol
    res[idd] = (best, sol)

if __name__ == "__main__":
    ci = CVRPInfo("fruitybun250.vrp")
    ci.visualise(ci.make_random_solution())
    # ci.write_infos()
    # best = 10000000
    # threads = []
    # res = [0 for _ in range(4)]
    # for i in range(0, 4):
    #     t = threading.Thread(target=worker, args=(ci, i, 2000, res))
    #     threads.append(t)
    #     t.start()
    # for i in range(4):
    #     threads[i].join()
    # print(min(res, key = lambda x: x[0]))
