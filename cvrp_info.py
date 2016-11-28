import os
import math
import random
import threading
from PIL import Image, ImageDraw

class Route(object):
    def __init__(self, route=[], cost=0, is_valid=False, demand=0):
        self.is_valid = is_valid
        self.route = route
        self.cost = cost
        self.demand = demand

    def insert_route(self, index, route):
        self.is_valid = False
        self.route = self.route[:index + 1] + route + self.route[index + 1:]

    def append_node(self, node):
        self.is_valid = False
        self.route = self.route[:-1] + [node] + [1]


    def remove_node(self, x):
        if x == 1:
            print("BAD")
            raw_input()
        self.is_valid = False
        del self.route[self.route.index(x)]


    def __repr__(self):
        debug_str = ", cost = " + str(self.cost) + ", demand = " + str(self.demand)
        ret_str = "->".join(str(n) for n in self.route)
        return ret_str + (debug_str if True else "")

class Solution(object):
    bad_count = 0

    def __init__(self, routes=[], cost=0, is_valid=False, demand=0):
        self.is_valid = is_valid
        self.routes = routes
        self.cost = cost
        self.demand = demand
        self.penalty = 0

    def shuffle(self):
        random.shuffle(self.routes)

    def remove_node(self, x):
        for route in self.routes:
            if x in route.route:
                route.remove_node(x)
        self.is_valid = False

    def insert_route(self, route_id, route_index, route):
        self.routes[route_id].insert_route(route_index, route)
        self.is_valid = False

    def random_subroute(self):
        r_i = random.randrange(0, len(self.routes))
        while len(self.routes[r_i].route) == 2:
            r_i = random.randrange(0, len(self.routes))
        c_s = random.randrange(1, len(self.routes[r_i].route))
        c_e = c_s
        while c_e == c_s:
            c_e = random.randrange(1, len(self.routes[r_i].route))
        if c_s > c_e:
            c_s, c_e = c_e, c_s
        return self.routes[r_i].route[c_s:c_e]

    def hash(self):
        return hash("-".join([",".join(str(x) for x in x.route) for x in self.routes]))

    def __repr__(self):
        return "\n".join([str(route) for route in self.routes])

class CVRPInfo(object):

    def __init__(self, data_file, debug=False):
        self.read_data(data_file)
        self.compute_dists()
        self.start_node = 1
        self.debug = debug
        self.max_route_len = 10
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
            nid, xc, yc = [float(x) for x in content[i].split()]
            self.coords[int(nid)] = (xc, yc)
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
        for xi in range(self.dimension + 1):
            for yi in range(self.dimension + 1):
                self.dist[xi][yi] = self.compute_dist(xi, yi)

    def bounding_box(self, route):
        x_min = min(self.coords[node][0] for node in route)
        x_max = max(self.coords[node][0] for node in route)
        y_min = min(self.coords[node][1] for node in route)
        y_max = max(self.coords[node][1] for node in route)
        return x_min, x_max, y_min, y_max

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
                        key=lambda x: self.dist[cur_route[-1] if random.uniform(0, 1) < 0.9 else 1][unserviced[x]])
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

    def refresh(self, solution):
        solution.cost, solution.demand = 0, 0
        for route_obj in solution.routes:
            route = route_obj.route
            route_obj.demand, route_obj.cost = 0, 0
            for i in range(0, len(route) - 1):
                route_obj.demand += self.demand[route[i]]
                route_obj.cost += self.dist[route[i]][route[i + 1]]
            solution.cost += route_obj.cost
            solution.demand += route_obj.demand
            if route_obj.demand > self.capacity:
                route_obj.is_valid = False
                solution.is_valid = False


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

    def visualise(self, solution):

        im = Image.new( 'RGB', (500,500), "white") # create a new black image
        draw = ImageDraw.Draw(im)
        color = (0, 0, 0)
        for i, route in enumerate(solution.routes):
            r_c = (i*i)%255
            g_c = (i*r_c)%255
            b_c = (i*g_c)%255
            nodes = route.route
            norm = lambda x, y: (2*x + 250, 2*y + 250)
            draw.line([norm(*self.coords[n]) for n in nodes], fill=(r_c, g_c, b_c), width=2)
        return im

if __name__ == "__main__":
    ci = CVRPInfo("fruitybun250.vrp")
    ci.visualise(ci.make_random_solution())
