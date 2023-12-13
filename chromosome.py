#chromsome interpretation
# 16 loops -> big actions (states) referred to as chrome
# Each loop has 8 genes (instructions/jump/action) referred to as gene
# Conditionals jump to other states
import random
import os
from os.path import exists
import shutil

def readChrome(chrome):
	loops = []
	for gene in chrome:
		#print("Current gene: {}".format(gene))
		
		loop = []		
		for instruction_gene in gene:
			#print("Current Instruction gene: {}".format(instruction_gene))
			
			
			if instruction_gene[0] == '1': # Case for jump chrom
				
				conditional_index = int(instruction_gene[1:5], 2)
				loop_number = int(instruction_gene[5:], 2)
				
			    # Structure: False, conditional index, jump to num	
				loop.append([False, conditional_index, loop_number])
				
				
				
				#print("Conditional loop: {}".format(conditional_index))
				#print("Loop number: {}".format(loop_number))
				
			else: # Case for action chromosome
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
#gene = [['100001111', '001111001', '010101101', '100111000']]
#chromosome = [['100001111', '001111001', '010101101', '000111000'], ['101111001', '000111000']]
#print(readChrome(chromosome))


# TODO : Add set conditional numbers
def generateChromosome():
    # Gene Size 9 bits
    # Loop size including conditional 8
    chromosome = []
    for loop in range(16):
        loop = []
        for i in range(8): # 8 genes per loop
            gene = ""
            for j in range(9): # gene size
                if i == 0 and j==0: 
                    gene += "1" 
                elif j == 0 :
                    gene += "0"
                else: 
                    gene += str(random.randint(0, 1))
            loop.append(gene)
        chromosome.append(loop)
    #print(chromosome)
    return chromosome
#generateChromosome()


def writeChromosomeToFile(chromosome, filename):
    dataPath = "data/" + filename
    print(dataPath)
    print(os.path.exists(dataPath))
    with open(dataPath, "w") as file:
         #for loop in chromosome:
            #for gene in loop:
        file.write(str(chromosome))

# Wipes data folder for each new run of core_controller
def createDataFolder():
	# Data folder
    try:
        shutil.rmtree("data/")
    except:
        pass
        
    os.mkdir("data/")
