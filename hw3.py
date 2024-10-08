import re
import random
from collections import deque

class Path:
    def __init__(self, path):
        self.path = path
    
    def set_size(self, size):
        self.size = size
    
    def set_fitness_score(self, fitness_score):
        self.fitness_score = fitness_score
    
    def set_target_node_count(self, target_node_count): # number of nodes from M in the path
        self.target_node_count = target_node_count
    
    def set_connected_target_count(self, connected_target_count): # number of nodes from M connected
        self.connected_target_count = connected_target_count
    
    def set_total_edges(self, total_edges):
        self.total_edges = total_edges
    
    def get_path(self):
        return self.path
    
    def get_fitness_score(self):
        return self.fitness_score

    def get_size(self):
        return self.size
    
    def get_target_node_count(self):
        return self.target_node_count

    def get_connected_target_count(self):
        return self.connected_target_count
    
    def get_total_edges(self):
        return self.total_edges

# function to make a dictionary representing a graph, where the number of links are used as keys
def dictionary_maker(file_name):
    with open (file_name, 'r') as file:
        graph = {}
        for line in file:
            if line.strip() and not line.strip().startswith('//'):
                match = re.search(r'(\d+)\s+(\d+)\s+//.*#(\d+)', line)

                if match:
                    node1 = int(match.group(1))
                    node2 = int(match.group(2))
                    edge_num = int(match.group(3))

                graph[edge_num] = (node1, node2)

    graph = {k:graph[k] for k in sorted (graph)}

    return graph

# function to make a random path (creating an individual component)
# based on the POPULATION_SIZE, loop this function to create population
def generate_path(graph):

    len_path = random.randint(1,len(graph))
    all_edge_numbers = list(range(0, len(graph)))

    random.shuffle(all_edge_numbers)
    edge_num_queue = deque(all_edge_numbers)

    path = []
    for i in range(len_path):
        path.append(edge_num_queue.pop())

    return path

def add_random_edges(graph, offspring, parent):
    # all the links (edges) in the graph
    graph_links = list(graph)
    random.shuffle(graph_links)
    graph_links_queue = deque(graph_links)

    for i in range(random.randint(1, len(parent.get_path()))):
        if (not graph_links_queue):
            break
        new_link = graph_links_queue.pop()
        while(new_link in offspring):
            if (not graph_links_queue):
                break
            new_link = graph_links_queue.pop()
        offspring.append(new_link)
    return offspring
            

# function to make a offspring path out of the two parent paths
def make_offspring(path1, path2, graph):
    # contain the links that comprises offspring
    offspring = []

    # all the links (edges) in the graph
    graph_links = list(graph)
    random.shuffle(graph_links)
    graph_links_queue = deque(graph_links)

    # all the links (edges) in the two paths
    all_links = path1.get_path() + path2.get_path()
    all_links = list(set(all_links)) # to prevent the duplication of the same link 
    random.shuffle(all_links) 
    all_links_queue = deque(all_links)

    prob = random.random()

    # make a offspring of the length of the path1
    if prob < 0.40:
        for i in range(random.randint(0, len(path1.get_path()))):
            offspring.append(all_links_queue.pop())
    # make a offspring of the length of the path2
    elif prob <0.80:
        for i in range(random.randint(0, len(path2.get_path()))):
            offspring.append(all_links_queue.pop())
    # make a offspring longer than the two paths
    else:
        # the idea is to first get an offspring of the same length as the longer parent path, and then, 
        #   add new links (the number of links is randomly decided less than the number of shorter path) to the offspring
        #   By randomly adding some links, it works as mutation
        if (len(path1.get_path()) < len(path2.get_path())):
            # first, get links for the number of length of the longer path (in his case, path2)
            for i in range(len(path2.get_path())):
                offspring.append(all_links_queue.pop())
            
            # additionally, add new links for the number of length less than that of the shorter path (in this case, path1)
            # for i in range(random.randint(1, len(path1.get_path()))):
            #     if (not graph_links_queue):
            #         break
            #     new_link = graph_links_queue.pop()
            #     while(new_link in offspring):
            #         if (not graph_links_queue):
            #             break
            #         new_link = graph_links_queue.pop()
            #     offspring.append(new_link)
            offspring = add_random_edges(graph, offspring, path1)

        else:
            # first, get links for the number of length of the longer path (in his case, path1)
            for i in range(len(path1.get_path())):
                if (not all_links_queue):
                    break
                offspring.append(all_links_queue.pop())

            # additionally, add new links for the number of length less than that of the shorter path (in this case, path1)
            # for i in range(random.randint(1, len(path2.get_path()))):
            #     if (not graph_links_queue):
            #         break
            #     new_link = graph_links_queue.pop()
            #     while(new_link in offspring):
            #         if (not graph_links_queue):
            #             break
            #         new_link = graph_links_queue.pop()
            #     offspring.append(new_link)
            offspring = add_random_edges(graph, offspring, path2)
    
    offspring = Path(offspring)

    return offspring

# function to generate a new generation. suppose that the parameter 'current_population' is 
#   already sorted based on fitness score
def make_new_generation(current_population, graph, target_nodes):
    # get the population size
    population_size = len(current_population)

    # store paths to be considered to be in new generation
    paths = current_population

    # store the paths for a new generation
    new_generation = []

    # store the new generated offspring paths
    offspring_paths = []

    # make offsprings first
    for i in range(population_size):
        # randomly select 2 parent paths out of the best 50% fitting paths
        parent_path1 = random.choice(current_population[0:(len(current_population)//2)])
        parent_path2 = random.choice(current_population[0:(len(current_population)//2)])

        offspring = make_offspring(parent_path1, parent_path2, graph)

        offspring.set_fitness_score(calc_fitness_score_joe(offspring.get_path(), graph, target_nodes))
        offspring_paths.append(offspring)
        offspring_paths.append(make_offspring(parent_path1, parent_path2, graph))

    # then, merge it with the current population
    paths.extend(offspring_paths)

    # sort it based on the fitness score.
    paths = sorted(paths, key=lambda path: path.fitness_score)

    # select the best paths for the number of the length of the current population, and make a new generation
    paths_queue = deque(paths)
    for i in range(population_size):
        new_generation.append(paths_queue.pop())

    # return the new population, here it is not sorted based on fitness score
    return new_generation



# DFS search through the graph
def dfs(node, graph, visited):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(neighbor, graph, visited)

# Function to see how many nodes are connected
def are_connected(edges, nodes):

    graph = {}
    for u, v in edges:
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []
        graph[u].append(v)
        graph[v].append(u)

    # Check if any nodes to check exist in the graph
    if not any(node in graph for node in nodes):
        return 0
    
    visited = set()
    for node in nodes:
        if node in graph:
            dfs(node, graph, visited)
            break  # Start DFS from the first existing node

    # Count how many of the nodes_to_check are in visited
    connected_count = sum(node in visited for node in nodes)

    return connected_count

# Calculates the fitness of the offspring
def calc_fitness_score(offspring, graph, target_nodes):
    offspring = [graph[key] for key in offspring]

    nodes_connected = are_connected(offspring, target_nodes)

    num_edges = len(offspring)

    fitness = nodes_connected/(1+num_edges)

    return fitness

def calc_fitness_score_joe(path, graph, target_nodes):
    path = [graph[key] for key in path]

    # number of nodes connected
    num_nodes_connected = are_connected(path, target_nodes)

    # number of edges in a path
    num_edges = len(path)

    # calculate the base score
    score = num_nodes_connected * 200

    # penalty depending on the length of the path (shorter path is better)
    score = score - num_edges * 20

    # if not all the target nodes are not connected, another penalty 
    if len(target_nodes) != num_nodes_connected:
        score = score - (len(target_nodes)-num_nodes_connected) * 200

    return score / len(target_nodes)


# Kiko
# Function to do Dijkstra search algorithm for fitness
# to check if a path is connected, and get the shortest path from one node
# this shows which nodes are connected to which nodes
def create_sub_graph(chromosome, graph):
    sub_graph = {}

    for c in chromosome:
        if not (graph[c][0] in sub_graph):
            sub_graph[graph[c][0]] = []
        sub_graph[graph[c][0]].append(graph[c][1])

        if not (graph[c][1] in sub_graph):
            sub_graph[graph[c][1]] = []
        sub_graph[graph[c][1]].append(graph[c][0])

    return sub_graph

def find_shortest_path(graph, start, goal):
    # Keep track of visited nodes
    visited = set()
    # Queue to store paths
    queue = deque([[start]])
    
    # BFS loop
    while queue:
        path = queue.popleft()
        node = path[-1]
        
        if node == goal:
            # TODO set in a path object
            return len(path) - 1  # Number of edges = number of nodes in path - 1
        
        if node not in visited:
            visited.add(node)
            for neighbor in graph[node]:
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    
    # TODO set in a path object
    return None  # Return None if no path exists

def calc_distance(sub_graph, visited_nodes):
    total_distance = 0
    connection_count = 1
    for i in range(len(visited_nodes)-1):
        distance = find_shortest_path(sub_graph, visited_nodes[i], visited_nodes[i+1])
        if distance != None:
            total_distance += distance
            connection_count += 1
    # TODO set in a path object
    return total_distance, connection_count
 
# Willy: function to calculate the fitness score 
"""
fun calc_fitness_score(chromsome):
    - if any node from M is in a chromsome
        - if there are more than two nodes in chromsome
            - if there are connections between them
                - cost of links
    - cost of links
"""

# Kiko: sort population based on fitness score
"""
fun sort_population():
    based on fitness score for each of chromsome, sort from the best to the worst
"""

# show each generation with graph colored
# show the best path from each generation
"""
fun show_generation(best_chromosome):
    - show with the library
"""

# function for main 
def __main__():
    graph = dictionary_maker('/Users/joejoezaki/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Documents/Semesters/Fall_2024/CSCE_480/hw/hw3/hw3/hw3_cost239.txt')

    # 1: the first population creation 
    population_size = 500

    target_nodes = [3, 9, ]

    new_population = []
    for i in range(population_size):
        path = Path(generate_path(graph))
        fitness_score = calc_fitness_score_joe(path.get_path(), graph, target_nodes)
        path.set_fitness_score(fitness_score)
        new_population.append(path)

    new_population = sorted(new_population, key=lambda path: path.fitness_score)

    

    print("------------- the 1st generation --------------")
    print(f"the best of this generation: {new_population[0].get_path()}, fitness score: {new_population[0].fitness_score}\n")
    
    # 2: check if the best path is found or not? if yes, show the result and the operation is done. 
    #       if not, proceed with the operations 
    #       - Here, we have to decide how to finish the operation. 
    #       - we can specify the number of operations, or we can end the operation 
    #           once a chromesome that seems to have the best fitting score is found in new generation

    # 3: conducting the mating process, and make new generation
    #   - once it is done, go back to the #2 and check if you have the path with the best fitting score. (while loop?)
    
    
    for k in range(100):
        new_population = make_new_generation(new_population, graph, target_nodes)
        # for i in range(5):
        #     print(f"the {i}th best of this generation: {new_population[i].get_path()}, fitness score: {new_population[i].fitness_score}\n")
        print(f"------------- best 5 solutions of {k+1}th generation")
        for i in range(5):
            print(f"{i}th: {new_population[i].get_path()}, {new_population[i].fitness_score}")

__main__()