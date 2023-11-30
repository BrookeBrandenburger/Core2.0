##Rough Program of CGA

import random

#Function to evaluate the fitness of an individual
def evaluate_fitness(individual):
    #Insert fitness Function

    return sum(individual)

#Cyclic Crossover
def cyclic_crossover(parent1, parent2):
    n = len(parent1) #Calcs the length of the parent genotype assuming both parents are the same length
    start = random.randint(0, n-1) #Generates a random starting index for the crossover process. The starting index is a random integer between 0 and 1
    child = [-1] * n #Serves as a gentotype for a list of -1 as a placeholder
    index = start #Initializes the random start for the index

    while child.count(-1) > 0: #Continues a loop until the placeholders are no longer there, so until the -1 isnt there anymore
        child[index] = parent[index] #This line copies the gene from parent1 at the current index to the corresponding parent in the phenotype
        index = parent2.index(parent1[index]) #This line updates the current index by finding the position of the same gene in 'parent2'. This step ensures the cyclic nature of the crossover

    return child

#Function for mutation
def mutate(individual):
    #Mutation logic goes here
    index1, index2 = random.sample(range(len(individual)), 2)
    individual[index1], individual[index2] = individual[index2], individual[index1]

#Main GA Loop
def cyclic_genetic_algorithm(population_size, generations):
    population = [[i for i in range (1,6)] for _ in range (population_size)] #Initialize

    for generation in range(generations):
        fitness_values = [evaluate_fitness(individuals) for individual in population]

        #Tournament Selection
        selected_parents = random.sample(list(range(population_size)), population_size//2)

        #Crossover
        offspring = []
        for i in range (0, len(selected_parents), 2):
            parent1- = population[selected_parents[i]]
            parent2 = population[selected_parents[i +. 1]]
            child = cyclic_crossover(parent1, parent2)
            offspring.append(child)

        #Mutation
        for individual in offspring:
            if random.random() < mutation_rate:
                mutate(individual)

        #Replacement (replace the old generation)
        population = offspring

        #Return the best individual at the end
        best_individual = max(population, key = evaluate_fitness)
        return best_individual

    #Example
    mutation_rate = 0.1
    best_solution = cyclic_genetic_algorithm(population_size=50, generations=100)
    print('Best Solution', best_solution)
    print('Fitness', evaluate_fitness(best_solution))



	
