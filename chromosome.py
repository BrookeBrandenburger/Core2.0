# chromsome interpretation
# 16 loops -> big actions (states) referred to as chrome
# Each loop has 8 genes (instructions/jump/action) referred to as gene
# Conditionals jump to other states
import random
import os
from os.path import exists
import shutil
from typing import List, Any, Union

class Evolver():
    @classmethod
    def crossover(cls, chromosome1, chromosome2):
        # Equal opprotunity for single point or uniform crossover
        chances = random.randint(0, 1)
        # chances = 0 #Used to manually set crossover type

        if chances == 1:  # Single Point Crossover: Occurs strictly between genes
            splicePoint = random.randint(1, len(chromosome1))
            chrome1_X = chromosome1[0:splicePoint]
            chrome1_Y = chromosome1[splicePoint:]
            # print(chrome1_X)
            chrome2_X = chromosome2[0:splicePoint]
            chrome2_Y = chromosome2[splicePoint:]

            child1 = chrome1_X + chrome2_Y
            child2 = chrome2_X + chrome1_Y
            #print("Child 1: {}".format(child1))
            #print("Child 2: {}".format(child2))

            if random.randint(0, 1) == 1:  # Randomly select a child to return
                return child1
            else:
                return child2
            # TODO ? Do we just select one for our new agent?

        elif chances == 0:  # Uniform crossover
            new_chromosome = []  # Full chromosome
            for loopIndex in range(len(chromosome1)):
                loop = []  # Loop containing 16 genes

                for geneIndex in range(len(chromosome1[loopIndex])):
                    gene = ""  # A 9 bit representation of a jump or action gene
                    for bitIndex in range(1, len(chromosome1[loopIndex][geneIndex])): # Start at one to not flip jump and actions
                        bit = ""
                        if 0 == random.randint(0, 1):  # Flip Bit!
                            bit = chromosome1[loopIndex][geneIndex][bitIndex]
                        else:
                            bit = chromosome2[loopIndex][geneIndex][bitIndex]

                        gene += bit
                    loop.append(gene)
                new_chromosome.append(loop)

            #print("Uniform Crossover Child: {}".format(new_chromosome))
            return new_chromosome

        else:
            print("Crossover error")


    # Mutation function based on a given chromosome and mutation rate
    @classmethod
    def mutate(cls, chromosome, MUT_RATE):

        new_chromosome: List[List[Any]] = []  # Full chromosome
        for loopIndex in range(len(chromosome)):
            loop = []  # Loop containing 16 genes

            for geneIndex in range(len(chromosome[loopIndex])):

                gene = ""  # A 9 bit representation of a jump or action gene
                for bit in chromosome[loopIndex][geneIndex][1:]:  # Start at one to keep action genes and jump genes defined
                    if 0 == random.randint(0, MUT_RATE):  # Mutate Time!
                        # Replaces 1 with 0 or 0 with 1
                        bit = '1' if bit == '0' else '0'
                    gene += bit
                loop.append(gene)
            new_chromosome.append(loop)

        return new_chromosome

    @classmethod
    def readChrome(cls, chrome):
        loops = []
        for gene in chrome:
            #print("Current gene: {}".format(gene))

            loop = []
            for instruction_gene in gene:
                #print("Current Instruction gene: {}".format(instruction_gene))

                if instruction_gene[0] == '1':  # Case for jump chrom

                    conditional_index = int(instruction_gene[1:5], 2)
                    loop_number = int(instruction_gene[5:], 2)

                # Structure: False, conditional index, jump to num
                    loop.append([False, conditional_index, loop_number])

                    #print("Conditional loop: {}".format(conditional_index))
                    #print("Loop number: {}".format(loop_number))

                else:  # Case for action chromosome
                    shoot = bool(int(instruction_gene[1]))
                    thrust = bool(int(instruction_gene[2]))
                    turn_quantity = int(instruction_gene[3:6], 2)
                    turn_target = int(instruction_gene[6:], 2)

                    #print("Shoot: {}".format(shoot))
                    #print("Thrust: {}".format(thrust))
                    #print("Turn Quantity: {}".format(turn_quantity))
                    #print("Turn Target: {}" .format(turn_target))

                    # If first val is true, action gene
                    loop.append([True, shoot, thrust, turn_quantity, turn_target])
            loops.append(loop)

        return loops

    # TODO : Add set conditional numbers
    @classmethod
    def generateChromosome(cls):
        # Gene Size 9 bits
        # Loop size including conditional 8
        chromosome = []
        for loop in range(16):
            loop = []
            for i in range(8):  # 8 genes per loop
                gene = ""
                for j in range(9):  # gene size
                    if i == 0 and j==0:
                        gene += "1"
                    elif j == 0 :
                        gene += "0"
                    else:
                        gene += str(random.randint(0, 1))
                loop.append(gene)
            chromosome.append(loop)
        # print(chromosome)
        return chromosome
    # generateChromosome()

    @classmethod
    def writeChromosomeToFile(cls, chromosome, filename):
        dataPath = "data/" + filename
        # print(dataPath)
        # print(os.path.exists(dataPath))
        with open(dataPath, "w") as file:
            # for loop in chromosome:
            # for gene in loop:
            file.write(str(chromosome))

    # Wipes data folder for each new run of core_controller

    @classmethod
    def createDataFolder(cls):
        # Data folder
        try:
            shutil.rmtree("data/")
        except:
            pass

        os.mkdir("data/")
