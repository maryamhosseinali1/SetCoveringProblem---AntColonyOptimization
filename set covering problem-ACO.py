#!/usr/bin/env python
# coding: utf-8

# # Set Covering problem using ACO

# # Maryam Hoseeinali 610398209

# ## general explanation:

# ### In this implementation, the minimum cost is calculated based on Ant Colony Optimization (ACO) in such a way that all elements of the universal set are covered.
# ### the algorithm works by iteratively constructing solution paths and updating the pheromone levels on the subsets based on the quality of the solutions found, algorithm is guided by the relative attractiveness and pheromone levels of the subsets, and it tends to converge to a good solution over time.

# ## import required libraries

# In[1]:


import numpy as np


# ## Graph class:

# ### set covering problem is represented using a graph structure. this representation used to capture the relation between the sets and elements
# ### each set in the set covering problem (it means each given subset of universal set) is represented as a vertex in the graph.
# ### the edges in the graph represent the relations between the sets based on their intersections.
# ### an edge exists between two sets if they have at least one common element.
# 
# ## initialization:
# ### -'set_costs' parameter is a list that contains the costs associated with each set.
# ### - 'sets_ph' represents the pheromone level for each set.
# ### - 'sets' is a list of sets where each set represents a subset of our universal set.
# ### - alpha and beta parameteres used in the calculation of set scores.
# 
# ## Graph methods:
# ### 1: calculate_set_attractiveness method  calculates the attractiveness of a set based on its intersection with the current set.
# ### 2: calculate_set_score method  calculates the score of a set based on its pheromone level and attractiveness.
# ### 3: select_from_sets method selects a set from available sets based on their scores and probabilities.
# ### 4: generate_path method generates a path by selecting sets until the current set is empty(all elements in cur_set are covered).
# ### 5: evaporate_nodes_pheromone method updates the pheromone level of each set by evaporating a certain percentage ofit (based on evaporation rate).
# ### 6: update_path_pheromone method updates the path pheromone level of each set based on the path and its cost.

# In[2]:


class Graph:
    def __init__(self, answer_path_length, sets, set_costs, alpha, beta):
        self.set_costs = set_costs
        self.sets_ph = {}
        self.sets = sets
        self.alpha = alpha
        self.beta = beta

## initializing pheromone levels
        for set_index in range(len(sets)):
        
## assigns an equal and positive pheromone level to all sets.
            self.sets_ph[set_index] = 1
        self.answer_path_length = answer_path_length

    def calculate_set_attractiveness(self, set_id, cur_set):
        return len(self.sets[set_id].intersection(cur_set)) / self.set_costs[set_id]

    def calculate_set_score(self, set_id, cur_set):
        pheromone_part = self.sets_ph[set_id]
        attractiveness_part = self.calculate_set_attractiveness(set_id, cur_set)
        return (self.alpha * pheromone_part) * (self.beta * attractiveness_part)
## calculate the score of a set

    def select_from_sets(self, cur_set):
        potential_sets = []
        probs = []
        total_score_sum = 0.0
        for set_id in range(len(self.sets)):
            if self.calculate_set_attractiveness(set_id, cur_set) == 0:
## it means the set does not cover any new elements.
                continue
            set_score = self.calculate_set_score(set_id, cur_set)
            potential_sets.append(set_id)
            total_score_sum += set_score
        for set_id in potential_sets:
            probs.append(self.calculate_set_score(set_id, cur_set) / total_score_sum)
        return np.random.choice(potential_sets, p=probs)
## randomly selects a set index from potential_sets based on the probs (probabilities)

    def generate_path(self):
        cur_set = set(range(self.answer_path_length))
        path_cost = 0
        path = []
        while cur_set:
            selected_set_id = self.select_from_sets(cur_set)
            path.append(selected_set_id)
            path_cost += self.set_costs[selected_set_id]
## updates the path and cost
            cur_set -= self.sets[selected_set_id]
## remove the covered elements from cur_set
        return path, path_cost

    def evaporate_nodes_pheromone(self, evp_rate):
        for set_index in range(len(self.sets)):
            self.sets_ph[set_index] = (1 - evp_rate) * self.sets_ph[set_index]

    def update_path_pheromone(self, path_info):
## path_info represents a solution path and its associated cost.
        path = path_info[0]
        path_cost = path_info[1]
        for set_id in path:
            self.sets_ph[set_id] += 1 / path_cost
## update pheromone level of the corresponding set.
## normalize the impact of the deposit based on the quality of the path
## Higher quality paths (lower path cost) receive a higher pheromone deposit.


# ## InputProcessor class:

# ### the InputProcessor class organizes the raw input data into a structured format that can be utilized by the set covering problem solver. 
# 

# In[3]:


class InputProcessor:
    @staticmethod
    def process_input(_input):
        n = _input[0]
        m = _input[1]
        costs = [0 for _ in range(m)]
        sets = [set() for _ in range(m)]
        for set_index in range(m):
            costs[set_index] = _input[set_index + 2]
        cur_ind = m + 2
        for element in range(n):
            element_cnt = _input[cur_ind]
            cur_ind += 1
            for _ in range(element_cnt):
                sets[_input[cur_ind] - 1].add(element)
                cur_ind += 1
        return n, m, costs, sets


# ## Solver class:

# ### The Solver class encapsulates the entire solving process. It initializes the necessary data structures, performs iterations of ant path generation, updates pheromone levels, and tracks the best solution found. By combining the Graph class with the ant colony optimization logic, the Solver class solves the problem and provides the best solution path along with its cost.

# In[4]:


class Solver:
    def __init__(self, solver_input):
        self.INF = 1000000000.0
        self.n, self.m, self.costs, self.sets = InputProcessor.process_input(solver_input)
## process input
        self.evp_rate = 0.5
        self.ants_count = 30
        self.alpha = 2
        self.beta = 1
## initialize parameters
        self.graph = Graph(self.n, self.sets, self.costs, self.alpha, self.beta)
## intialize the Graph object graph with the extracted data.


    def solve(self):
        answer_path = []
        answer_path_cost = self.INF
        for epoch in range(30):
            print("############# epoch:", str(epoch), "#############")
            best_cost = self.INF
            best_path = []
## track the best path and its cost
            for path_ind in range(self.ants_count):
                path, path_cost = self.graph.generate_path()
## each ant selects sets based onpheromone levels and set attractiveness.
                if path_cost < best_cost:
                    best_cost = path_cost
                    best_path = path
                self.graph.update_path_pheromone([path, path_cost])
            if best_cost < answer_path_cost:
                answer_path = [best_path, best_cost]
                answer_path_cost = best_cost
## checks if the best_cost found in this epoch is better than previous one
## if it was it updates answer_path and answer_path_cost
            self.graph.evaporate_nodes_pheromone(self.evp_rate)
## reducing the pheromone levels by evaporation rate.
            print("Epoch best answer cost:", best_cost)
            print("Global best answer cost:", answer_path[1])
        print("Answer")
        print(answer_path[0])
        print("Cost:", answer_path[1])


        


# In[6]:


input_file_name = input("Please enter input file name: ")
with open(input_file_name, "r") as inputFile:
    lines = inputFile.readlines()
    clean_input = []
    for line in lines:
        numbers = list(map(int, line.rstrip().split()))
        clean_input += numbers
    solver = Solver(solver_input=clean_input)
    solver.solve()


# In[9]:


input_file_name = input("Please enter input file name: ")
with open(input_file_name, "r") as inputFile:
    lines = inputFile.readlines()
    clean_input = []
    for line in lines:
        numbers = list(map(int, line.rstrip().split()))
        clean_input += numbers
    solver = Solver(solver_input=clean_input)
    solver.solve()


# In[10]:


input_file_name = input("Please enter input file name: ")
with open(input_file_name, "r") as inputFile:
    lines = inputFile.readlines()
    clean_input = []
    for line in lines:
        numbers = list(map(int, line.rstrip().split()))
        clean_input += numbers
    solver = Solver(solver_input=clean_input)
    solver.solve()


# In[ ]:




