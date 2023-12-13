import libpyAI as ai
import math
import random
import random
import os 
from os import path

from chromosome import *

def findAngle(X, ENEMY_X, ENEMY_DIST):  # Taking the X coordinates of agent and enemy
    hyp = ENEMY_DIST
    if ENEMY_X - X > 0:
        x_dist = ENEMY_X - X
    else:
        x_dist = X - ENEMY_X
    theta = int(math.degrees(math.acos(x_dist / hyp))) - 90

    return theta

def initializeAgent(input_chrome = generateChromosome()):
    # Chomosome Controllers! #[[loop1], [loop2]]
    global chrome # Decoded chromosome
    global raw_chrome_values
    global current_loop # A chromosome is made up of 16 loops
    global current_loop_idx
    global current_gene_idx # Refers to an action within a loop (jump/action)
    global chromosome
    global prev_score
    global score

    prev_score = 0
    score = 0

    chromosome = input_chrome
    #writeChromosomeToFile(chromosome, "output_chromosome.txt")#Can call whatever 
    #chrome = readChrome(chromosome)
    #current_loop_idx = 0 # Current Loop Number
    #current_loop = chrome[current_loop_idx]
    #current_gene_idx = 0 # Current gene Number within a given loop

def earnedKill(ai):
    global score
    global prev_score
    global chromosome
   
    filename = "selChrome_0.txt"

    while os.path.exists(("data/" + filename)):
        index = int((filename.split("_")[1]).split(".")[0]) # Get the number at end of file name
        index = str(index+1)
        filename = "selChrome_{}.txt".format(index)

    # Score increment indicates a kill
    if score > prev_score:
        writeChromosomeToFile(chromosome, filename)
        ai.talk('New Chrome File -' + filename)

def died(ai):
    global score
    global prev_score
    global chromosome
    
    message = (ai.scanMsg(0)).split("-")
    # Score change and message with hyphen (indicating killed instead of wall collision)
    if score != prev_score: 
        if len(message) > 1:
            print("Death and death message found")
            print(message)
            new_chromosome_file_name = "data/" + str(message[1])

            new_chromosome = None
            with open(new_chromosome_file_name, 'r') as f:
                new_chromosome = eval(f.read())

            initializeAgent(new_chromosome)


def AI_loop():
    try:

        global current_loop_idx
        global chrome # Decoded chromosome
        global current_loop
        global current_gene_idx
        global chromosome
	    
        
        # Kill/Death Tracking
        global score
        global prev_score
        earnedKill(ai) # Check for kill
        died(ai) # If killed, get new chromosome

        # NOTE: Do we want to crossover with a random new chroomsome if we crash ourselves?
        prev_score = score
        score = ai.selfScore()

        closestShipId = int(ai.closestShipId())
        X = ai.selfX()
        ENEMY_SPEED = None
        ENEMY_DIST = None
        ENEMY_X = None
        ENEMY_Y = None
        ENEMY_HEADING = None

        if closestShipId != -1:
            ENEMY_SPEED = float(ai.enemySpeedId(closestShipId))
            ENEMY_DIST = float(ai.enemyDistanceId(closestShipId))
            ENEMY_X = int(ai.screenEnemyXId(closestShipId))
            ENEMY_Y = int(ai.screenEnemyYId(closestShipId))
            ENEMY_HEADING = float(ai.enemyHeadingDegId(closestShipId))

        print("Enemy_X: {}".format(ENEMY_X))
        print("Enemy_Y: {}".format(ENEMY_Y))

        if ENEMY_DIST != None:
            print("Theta: {}".format(findAngle(X, ENEMY_X, ENEMY_DIST)))



    except Exception as e:
        print("Exception")
        print(e)
        ai.quitAI()

def main():
    initializeAgent([['110111110', '010011011', '000111111', '001011000', '010110011', '010011110', '000001011', '010101000'], ['101010101', '011001100', '010111010', '000001010', '010100100', '000100100', '010100000', '010011101'], ['110000010', '011101110', '001100011', '001010011', '001111100', '000000000', '001111011', '010111000'], ['101011001', '010000000', '011011111', '001100011', '000111001', '001010001', '000111111', '011000111'], ['100101111', '001011111', '011011011', '001110000', '010101100', '010100000', '010101101', '000011010'], ['100010000', '000111100', '000100010', '000011100', '010111000', '011100011', '011111111', '000100010'], ['100011001', '001101101', '001100011', '000001100', '001100011', '000010101', '000111101', '011101000'], ['100001001', '001010011', '000000001', '011000011', '001110010', '010011011', '011110011', '011110110'], ['110110000', '011110001', '011100110', '011010110', '000011001', '011111101', '010100110', '010100010'], ['110001011', '000100111', '011101101', '001010001', '010101101', '010001000', '000011000', '010110111'], ['111010011', '000100010', '011010000', '010011000', '000011111', '000110110', '011100000', '011001000'], ['110110111', '011011101', '000100111', '011100001', '010100111', '010011001', '001000101', '001010100'], ['111000111', '000010111', '011110100', '000111011', '011101110', '001110010', '011101010', '010000001'], ['101111010', '001101010', '000011111', '001011110', '011000001', '000001001', '010111100', '001001010'], ['111001001', '011100010', '011010100', '000101110', '011110100', '010010100', '001000010', '001101110'], ['100011101', '010011010', '000101111', '000010101', '010101000', '010110100', '001110101', '011000111']])
    # Tester chromosome - varying behavior, seemms to spin in circles at low speeds near other bots

    ai.start(AI_loop, ["-name", "HumanCore", "-join", "localhost"])


if __name__ =="__main__":
    main()
